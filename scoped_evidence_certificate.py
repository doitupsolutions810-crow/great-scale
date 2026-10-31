"""CXVI: scoped evidence certificates that keep uncertainty explicit."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
from evidence_scope_binding import evaluate_scope_binding

SCHEMA = "great-scale-scoped-evidence-certificate-v1"
STATE_VALUES = {"MATCH", "MISMATCH", "UNKNOWN"}
LINEAGE_VALUES = {"SAME", "ORDERED", "FORK", "INCOMPARABLE", "NOT_ASSESSED"}
AUTH_VALUES = {"VERIFIED", "UNVERIFIED", "NOT_ASSESSED"}


def build_evidence_certificate(*, state_equivalence: str,
        lineage_relation: str, observed_count: int,
        declared_count: int | None, scope_complete: bool,
        authenticity_status: str, distinct_signers: int = 0,
        signer_threshold: int = 0, evidence_ids: Sequence[str] = (),
        trust_basis: str | None = None,
        assumptions: Sequence[str] = (),
        scope_manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Classify evidence within a declared scope; this function verifies no signatures.

    A caller may use authenticity_status='VERIFIED' only after its own trusted
    verifier has validated the evidence and trust policy. This function records
    that assertion; it does not establish cryptographic authenticity itself.
    """
    if state_equivalence not in STATE_VALUES:
        raise ValueError("invalid state_equivalence")
    if lineage_relation not in LINEAGE_VALUES:
        raise ValueError("invalid lineage_relation")
    if authenticity_status not in AUTH_VALUES:
        raise ValueError("invalid authenticity_status")
    for name, value in (("observed_count", observed_count),
                        ("distinct_signers", distinct_signers),
                        ("signer_threshold", signer_threshold)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    if declared_count is not None and (isinstance(declared_count, bool) or not isinstance(declared_count, int) or declared_count < 0):
        raise ValueError("declared_count must be a non-negative integer or None")
    if declared_count is not None and observed_count > declared_count:
        raise ValueError("observed_count cannot exceed declared_count")
    if not isinstance(scope_complete, bool):
        raise ValueError("scope_complete must be boolean")
    if scope_complete and (declared_count is None or observed_count != declared_count):
        raise ValueError("complete scope requires observed_count == declared_count")
    if authenticity_status == "VERIFIED":
        if signer_threshold < 1 or distinct_signers < signer_threshold:
            raise ValueError("verified authenticity requires signer threshold to be met")
        if not isinstance(trust_basis, str) or not trust_basis.strip():
            raise ValueError("verified authenticity requires a non-empty trust_basis")
    ids = list(evidence_ids)
    if any(not isinstance(x, str) or not x.strip() for x in ids):
        raise ValueError("evidence_ids must contain non-empty strings")
    if len(ids) != len(set(ids)):
        raise ValueError("evidence_ids must be unique")
    scope_binding = None
    if scope_manifest is not None:
        if len(ids) != observed_count:
            raise ValueError("evidence_ids length must equal observed_count when scope_manifest is supplied")
        scope_binding = evaluate_scope_binding(scope_manifest, ids)
        if scope_binding["status"] != "EXACT_MANIFEST_MATCH":
            scope_complete = False

    assumptions_list = list(assumptions)
    if any(not isinstance(x, str) or not x.strip() for x in assumptions_list):
        raise ValueError("assumptions must contain non-empty strings")

    # Contradiction in observed evidence dominates absence elsewhere (CXII).
    if state_equivalence == "MISMATCH" or lineage_relation == "FORK":
        disposition = "CONFLICT_WITHIN_OBSERVED_EVIDENCE"
    elif (scope_binding is not None and scope_binding["status"] in {"INVALID_MANIFEST", "SCOPE_MISMATCH"}):
        disposition = "UNRESOLVED"
    elif (state_equivalence != "MATCH" or lineage_relation not in {"SAME", "ORDERED"}
          or authenticity_status != "VERIFIED"):
        disposition = "UNRESOLVED"
    elif not scope_complete:
        disposition = "PARTIAL_EVIDENCE"
    else:
        disposition = "CONSISTENT_WITHIN_DECLARED_SCOPE"

    return {
        "schema": SCHEMA,
        "state_equivalence": state_equivalence,
        "lineage_relation": lineage_relation,
        "population": {
            "observed_count": observed_count,
            "declared_count": declared_count,
            "scope_complete": scope_complete,
        },
        "authenticity": {
            "status": authenticity_status,
            "distinct_signers": distinct_signers,
            "signer_threshold": signer_threshold,
            "trust_basis": trust_basis if authenticity_status == "VERIFIED" else None,
        },
        "evidence_ids": ids,
        "scope_binding": scope_binding,
        "assumptions": assumptions_list,
        "disposition": disposition,
        "claim_scope": "declared population only; no claim about unseen records or unstated trust assumptions",
    }
