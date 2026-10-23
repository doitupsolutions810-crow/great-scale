"""CXVII: bind observed evidence to a content-addressed declared scope.

The digest binds bytes/fields to a manifest; it does not prove that the
manifest's issuer enumerated the real-world population completely.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

SCHEMA = "great-scale-evidence-scope-manifest-v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _nonempty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _ids(values: Sequence[str], name: str) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of IDs, not a string")
    result = list(values)
    if not result:
        raise ValueError(f"{name} must contain at least one ID")
    if any(not isinstance(item, str) or not item.strip() for item in result):
        raise ValueError(f"{name} must contain non-empty strings")
    result = [item.strip() for item in result]
    if len(result) != len(set(result)):
        raise ValueError(f"{name} must not contain duplicate IDs")
    return result


def _payload(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {key: manifest[key] for key in (
        "schema", "scope_id", "declared_evidence_ids", "declared_count",
        "policy_id", "policy_version", "authority_ref"
    )}


def build_scope_manifest(*, scope_id: str, declared_evidence_ids: Sequence[str],
                         policy_id: str, policy_version: str,
                         authority_ref: str) -> dict[str, Any]:
    """Create a deterministic manifest for a declared evidence population."""
    ids = sorted(_ids(declared_evidence_ids, "declared_evidence_ids"))
    payload = {
        "schema": SCHEMA,
        "scope_id": _nonempty(scope_id, "scope_id"),
        "declared_evidence_ids": ids,
        "declared_count": len(ids),
        "policy_id": _nonempty(policy_id, "policy_id"),
        "policy_version": _nonempty(policy_version, "policy_version"),
        "authority_ref": _nonempty(authority_ref, "authority_ref"),
    }
    return {**payload, "manifest_digest": hashlib.sha256(_canonical(payload)).hexdigest()}


def evaluate_scope_binding(manifest: Mapping[str, Any],
                           observed_evidence_ids: Sequence[str]) -> dict[str, Any]:
    """Compare observed IDs to a manifest without claiming external completeness.

    The output distinguishes an exact set match, missing declared evidence,
    extra/out-of-scope evidence, and an invalid or tampered manifest.
    """
    if not isinstance(manifest, Mapping):
        raise ValueError("manifest must be a mapping")
    observed = _ids(observed_evidence_ids, "observed_evidence_ids")
    required = ("schema", "scope_id", "declared_evidence_ids", "declared_count",
                "policy_id", "policy_version", "authority_ref", "manifest_digest")
    if any(key not in manifest for key in required):
        return {"schema": "great-scale-evidence-scope-binding-result-v1",
                "status": "INVALID_MANIFEST", "reason": "required field missing",
                "scope_id": manifest.get("scope_id"), "manifest_digest": None,
                "missing_ids": [], "extra_ids": [],
                "external_completeness_proven": False}
    try:
        declared = sorted(_ids(manifest["declared_evidence_ids"], "declared_evidence_ids"))
        payload = _payload(manifest)
        expected_digest = hashlib.sha256(_canonical(payload)).hexdigest()
        structurally_valid = (
            manifest["schema"] == SCHEMA
            and manifest["declared_count"] == len(declared)
            and manifest["declared_evidence_ids"] == declared
            and isinstance(manifest["manifest_digest"], str)
            and manifest["manifest_digest"] == expected_digest
        )
    except (TypeError, ValueError, KeyError):
        structurally_valid = False
        declared = []
    if not structurally_valid:
        return {"schema": "great-scale-evidence-scope-binding-result-v1",
                "status": "INVALID_MANIFEST", "reason": "schema, count, ordering, or digest validation failed",
                "scope_id": manifest.get("scope_id"), "manifest_digest": manifest.get("manifest_digest"),
                "missing_ids": [], "extra_ids": [],
                "external_completeness_proven": False}

    missing = sorted(set(declared) - set(observed))
    extra = sorted(set(observed) - set(declared))
    if extra:
        status = "SCOPE_MISMATCH"
    elif missing:
        status = "PARTIAL_SCOPE"
    else:
        status = "EXACT_MANIFEST_MATCH"
    return {
        "schema": "great-scale-evidence-scope-binding-result-v1",
        "status": status,
        "scope_id": manifest["scope_id"],
        "manifest_digest": manifest["manifest_digest"],
        "declared_count": len(declared),
        "observed_count": len(observed),
        "missing_ids": missing,
        "extra_ids": extra,
        "policy_id": manifest["policy_id"],
        "policy_version": manifest["policy_version"],
        "authority_ref": manifest["authority_ref"],
        "external_completeness_proven": False,
        "interpretation": "Exactness is relative to this declared manifest; authority and real-world population completeness require independent verification.",
    }
