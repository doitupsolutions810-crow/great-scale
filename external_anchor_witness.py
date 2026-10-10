"""External anchoring for Great Scale audit-trace heads.

This module creates a canonical SHA-256 commitment and verifies an Ed25519
witness signature over it. The private key must be held by an independently
controlled witness. This code does not provide trusted time, key custody,
network publication, or statistical-null validation.
"""
from __future__ import annotations
import hashlib, json
from typing import Any


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def trace_commitment(trace: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(trace)).hexdigest()

def create_anchor_statement(trace: dict[str, Any], sequence: int, previous_anchor: str | None = None) -> dict[str, Any]:
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise ValueError("sequence must be a positive integer")
    if previous_anchor is not None and (not isinstance(previous_anchor, str) or len(previous_anchor) != 64):
        raise ValueError("previous_anchor must be a 64-character hex digest or None")
    commitment = trace_commitment(trace)
    return {"schema": "great-scale-external-anchor-v1", "sequence": sequence,
            "previous_anchor": previous_anchor, "trace_commitment": commitment}

def sign_anchor(statement: dict[str, Any], private_key: Any) -> dict[str, Any]:
    """Sign with cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PrivateKey."""
    signature = private_key.sign(canonical_bytes(statement))
    return {"statement": statement, "signature_hex": signature.hex()}

def verify_anchor(anchor: dict[str, Any], public_key: Any, trace: dict[str, Any], expected_sequence: int,
                  expected_previous_anchor: str | None = None) -> dict[str, Any]:
    try:
        statement = anchor["statement"]
        if statement.get("schema") != "great-scale-external-anchor-v1":
            return {"valid": False, "reason": "unsupported schema"}
        if statement.get("sequence") != expected_sequence or statement.get("previous_anchor") != expected_previous_anchor:
            return {"valid": False, "reason": "anchor sequence or predecessor mismatch"}
        if statement.get("trace_commitment") != trace_commitment(trace):
            return {"valid": False, "reason": "trace commitment mismatch"}
        public_key.verify(bytes.fromhex(anchor["signature_hex"]), canonical_bytes(statement))
        return {"valid": True, "sequence": expected_sequence, "trace_commitment": statement["trace_commitment"]}
    except Exception:
        return {"valid": False, "reason": "malformed anchor or signature verification failed"}
