"""CXI: compare independently signed observer views with quorum safeguards.

This layer supplements CX checkpoint pairwise comparison. It requires distinct
signer identities and can require distinct configured fault domains. It reports
what the supplied signed records establish; it does not prove operational
independence, trusted time, publication completeness, or scientific validity.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping, Sequence
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from observer_checkpoint_consistency import compare_checkpoints, verify_checkpoint


def compare_observer_views(
    checkpoints: Sequence[Mapping[str, Any]],
    trusted_signers: Mapping[str, Ed25519PublicKey],
    *,
    minimum_distinct_signers: int = 2,
    signer_fault_domains: Mapping[str, str] | None = None,
    minimum_fault_domains: int = 1,
) -> dict[str, Any]:
    """Classify a supplied set of signed checkpoints conservatively.

    Raises ValueError for invalid signatures, duplicate signer IDs, invalid
    policy thresholds, or insufficient signer/domain quorum. Returns FORK if
    any pair conflicts; CONSISTENT only if every pair is SAME or ORDERED;
    otherwise returns INCOMPARABLE. A quorum is a policy gate, not proof that
    signers are actually independent.
    """
    if isinstance(minimum_distinct_signers, bool) or not isinstance(minimum_distinct_signers, int) or minimum_distinct_signers < 1:
        raise ValueError("minimum_distinct_signers must be a positive integer")
    if isinstance(minimum_fault_domains, bool) or not isinstance(minimum_fault_domains, int) or minimum_fault_domains < 1:
        raise ValueError("minimum_fault_domains must be a positive integer")
    if not checkpoints:
        raise ValueError("at least one checkpoint is required")

    signer_ids: list[str] = []
    for checkpoint in checkpoints:
        if not verify_checkpoint(checkpoint, trusted_signers):
            raise ValueError("all checkpoints must have valid signatures from trusted signers")
        signer_id = checkpoint.get("signer_id")
        if not isinstance(signer_id, str) or not signer_id:
            raise ValueError("checkpoint signer_id must be non-empty")
        signer_ids.append(signer_id)

    distinct_signers = set(signer_ids)
    if len(distinct_signers) != len(signer_ids):
        raise ValueError("each observer view must come from a distinct signer")
    if len(distinct_signers) < minimum_distinct_signers:
        raise ValueError("insufficient distinct signer quorum")

    domains: set[str] = set()
    if signer_fault_domains is not None:
        for signer_id in distinct_signers:
            domain = signer_fault_domains.get(signer_id)
            if not isinstance(domain, str) or not domain.strip():
                raise ValueError(f"missing fault-domain mapping for signer {signer_id}")
            domains.add(domain)
        if len(domains) < minimum_fault_domains:
            raise ValueError("insufficient distinct fault-domain quorum")
    elif minimum_fault_domains > 1:
        raise ValueError("fault-domain mapping is required when minimum_fault_domains > 1")

    pair_results: list[dict[str, str]] = []
    overall = "CONSISTENT"
    for (i, a), (j, b) in combinations(enumerate(checkpoints), 2):
        relation = compare_checkpoints(a, b, trusted_signers)
        pair_results.append({"left_signer": signer_ids[i], "right_signer": signer_ids[j], "relation": relation})
        if relation == "FORK":
            overall = "FORK"
        elif relation == "INCOMPARABLE" and overall != "FORK":
            overall = "INCOMPARABLE"

    return {
        "schema": "great-scale-observer-view-comparison-v1",
        "classification": overall,
        "observer_count": len(checkpoints),
        "distinct_signer_count": len(distinct_signers),
        "distinct_fault_domain_count": len(domains) if signer_fault_domains is not None else None,
        "pairwise_results": pair_results,
        "scope": "classification of supplied signed checkpoints only",
        "limitations": [
            "distinct signer IDs do not prove independent key custody or operators",
            "fault-domain labels are caller-supplied policy metadata, not independently attested",
            "CONSISTENT does not prove that no unseen conflicting checkpoint exists",
            "no trusted timestamp, global publication, or scientific validity is established",
        ],
    }
