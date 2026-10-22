"""CVI: threshold-signed external checkpoints for Great Scale evidence traces."""
from __future__ import annotations
import hashlib, json
from typing import Any, Mapping
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

SCHEMA = "great-scale-threshold-checkpoint-v1"

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def trace_commitment(trace: Any) -> str:
    return hashlib.sha256(canonical_json(trace)).hexdigest()

def checkpoint_statement(trace: Any, sequence: int, previous_anchor: str | None = None) -> dict[str, Any]:
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
        raise ValueError("sequence must be a non-negative integer")
    if previous_anchor is not None and not isinstance(previous_anchor, str):
        raise ValueError("previous_anchor must be a string or None")
    return {"schema": SCHEMA, "sequence": sequence, "previous_anchor": previous_anchor, "trace_commitment": trace_commitment(trace)}

def sign_statement(statement: Mapping[str, Any], witness_id: str, private_key: Ed25519PrivateKey) -> dict[str, str]:
    if not witness_id or not isinstance(witness_id, str):
        raise ValueError("witness_id must be a non-empty string")
    return {"witness_id": witness_id, "signature": private_key.sign(canonical_json(dict(statement))).hex()}

def create_checkpoint(trace: Any, sequence: int, witnesses: Mapping[str, Ed25519PrivateKey], previous_anchor: str | None = None) -> dict[str, Any]:
    statement = checkpoint_statement(trace, sequence, previous_anchor)
    return {"statement": statement, "signatures": [sign_statement(statement, wid, key) for wid, key in sorted(witnesses.items())]}

def verify_checkpoint(checkpoint: Mapping[str, Any], trace: Any, public_keys: Mapping[str, Ed25519PublicKey], threshold: int, expected_sequence: int, expected_previous_anchor: str | None = None) -> bool:
    """True iff at least threshold distinct trusted keys verify the exact expected statement."""
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError("threshold must be a positive integer")
    if threshold > len(public_keys):
        raise ValueError("threshold cannot exceed the trusted witness registry")
    if not isinstance(checkpoint, Mapping):
        raise ValueError("checkpoint must be a mapping")
    statement, signatures = checkpoint.get("statement"), checkpoint.get("signatures")
    if not isinstance(statement, Mapping) or not isinstance(signatures, list):
        raise ValueError("checkpoint requires statement and signatures list")
    expected = checkpoint_statement(trace, expected_sequence, expected_previous_anchor)
    if dict(statement) != expected:
        return False
    seen, valid = set(), 0
    payload = canonical_json(dict(statement))
    for item in signatures:
        if not isinstance(item, Mapping):
            raise ValueError("each signature entry must be a mapping")
        wid, sig = item.get("witness_id"), item.get("signature")
        if not isinstance(wid, str) or not wid:
            raise ValueError("signature entry has invalid witness_id")
        if wid in seen:
            raise ValueError(f"duplicate witness identity: {wid}")
        seen.add(wid)
        key = public_keys.get(wid)
        if key is None or not isinstance(sig, str):
            continue
        try:
            key.verify(bytes.fromhex(sig), payload)
        except (InvalidSignature, ValueError):
            continue
        valid += 1
    return valid >= threshold
