"""CXI: independently signed observer gossip and checkpoint conflict detection."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from threshold_witness_checkpoint import canonical_json
from observer_checkpoint_consistency import verify_checkpoint, checkpoint_id

RECEIPT_SCHEMA = "great-scale-cxi-observation-v1"

def observation_body(observer_id: str, checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(observer_id, str) or not observer_id.strip():
        raise ValueError("observer_id must be non-empty")
    return {"schema": RECEIPT_SCHEMA, "observer_id": observer_id, "checkpoint_id": checkpoint_id(checkpoint), "checkpoint": {"body": dict(checkpoint["body"]), "signer_id": checkpoint["signer_id"], "signature": checkpoint["signature"]}}

def sign_observation(observer_id: str, checkpoint: Mapping[str, Any], key: Ed25519PrivateKey) -> dict[str, Any]:
    body = observation_body(observer_id, checkpoint)
    return {"body": body, "signature": key.sign(canonical_json(body)).hex()}

def verify_observation(receipt: Mapping[str, Any], trusted_observers: Mapping[str, Ed25519PublicKey], trusted_log_signers: Mapping[str, Ed25519PublicKey]) -> bool:
    if not isinstance(receipt, Mapping) or not isinstance(receipt.get("body"), Mapping):
        return False
    body = dict(receipt["body"])
    if body.get("schema") != RECEIPT_SCHEMA:
        return False
    observer_id = body.get("observer_id")
    key = trusted_observers.get(observer_id) if isinstance(observer_id, str) else None
    cp = body.get("checkpoint")
    if key is None or not isinstance(cp, Mapping) or not verify_checkpoint(cp, trusted_log_signers):
        return False
    try:
        if body != observation_body(observer_id, cp):
            return False
        key.verify(bytes.fromhex(receipt.get("signature", "")), canonical_json(body))
    except (InvalidSignature, ValueError, TypeError, KeyError):
        return False
    return True

def analyze_observations(receipts: Sequence[Mapping[str, Any]], trusted_observers: Mapping[str, Ed25519PublicKey], trusted_log_signers: Mapping[str, Ed25519PublicKey], minimum_observers: int = 2) -> dict[str, Any]:
    """Analyze only verified, unique observers; classify conflicts per log and size."""
    if isinstance(minimum_observers, bool) or not isinstance(minimum_observers, int) or minimum_observers < 1:
        raise ValueError("minimum_observers must be a positive integer")
    accepted: dict[str, Mapping[str, Any]] = {}
    rejected = 0
    duplicate_ids: set[str] = set()
    for receipt in receipts:
        if not verify_observation(receipt, trusted_observers, trusted_log_signers):
            rejected += 1
            continue
        body = receipt["body"]
        observer = body["observer_id"]
        if observer in accepted:
            duplicate_ids.add(observer)
            continue
        accepted[observer] = body["checkpoint"]
    buckets: dict[tuple[str, int], dict[str, set[str]]] = {}
    for observer, cp in accepted.items():
        b = cp["body"]
        buckets.setdefault((b["log_id"], b["size"]), {}).setdefault(b["head_hash"], set()).add(observer)
    conflicts = []
    for (log_id, size), heads in sorted(buckets.items()):
        if len(heads) > 1:
            conflicts.append({"log_id": log_id, "size": size, "competing_heads": [{"head_hash": h, "observers": sorted(ids)} for h, ids in sorted(heads.items())]})
    enough = len(accepted) >= minimum_observers
    return {"status": "FORK_DETECTED" if conflicts else ("NO_CONFLICT_OBSERVED" if enough else "INSUFFICIENT_OBSERVERS"), "verified_observer_count": len(accepted), "minimum_observers": minimum_observers, "rejected_receipts": rejected, "duplicate_observer_ids": sorted(duplicate_ids), "conflicts": conflicts, "scope_note": "No conflict observed is not proof of global consistency; results cover only verified receipts supplied to this analysis."}
