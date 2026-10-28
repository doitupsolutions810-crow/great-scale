"""CX: signed observer checkpoints and detectable registry-log forks."""
from __future__ import annotations
from typing import Any, Mapping
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from threshold_witness_checkpoint import canonical_json
from registry_transition_chain import registry_digest, GENESIS_PARENT

CHECKPOINT_SCHEMA = "great-scale-observer-checkpoint-v1"

def checkpoint_body(log_id: str, size: int, head_hash: str, previous_checkpoint_hash: str = GENESIS_PARENT) -> dict[str, Any]:
    if not isinstance(log_id, str) or not log_id.strip():
        raise ValueError("log_id must be non-empty")
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("size must be a positive integer")
    for name, value in (("head_hash", head_hash), ("previous_checkpoint_hash", previous_checkpoint_hash)):
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} must be non-empty")
    return {"schema": CHECKPOINT_SCHEMA, "log_id": log_id, "size": size, "head_hash": head_hash, "previous_checkpoint_hash": previous_checkpoint_hash}

def sign_checkpoint(body: Mapping[str, Any], signer_id: str, private_key: Ed25519PrivateKey) -> dict[str, Any]:
    if not isinstance(signer_id, str) or not signer_id.strip():
        raise ValueError("signer_id must be non-empty")
    normalized = dict(body)
    return {"body": normalized, "signer_id": signer_id, "signature": private_key.sign(canonical_json(normalized)).hex()}

def verify_checkpoint(checkpoint: Mapping[str, Any], trusted_signers: Mapping[str, Ed25519PublicKey]) -> bool:
    if not isinstance(checkpoint, Mapping) or not isinstance(checkpoint.get("body"), Mapping):
        raise ValueError("checkpoint must contain body")
    body = dict(checkpoint["body"])
    if body.get("schema") != CHECKPOINT_SCHEMA:
        return False
    try:
        if checkpoint_body(body.get("log_id"), body.get("size"), body.get("head_hash"), body.get("previous_checkpoint_hash")) != body:
            return False
    except (ValueError, TypeError):
        return False
    signer_id, signature = checkpoint.get("signer_id"), checkpoint.get("signature")
    key = trusted_signers.get(signer_id) if isinstance(signer_id, str) else None
    if key is None or not isinstance(signature, str):
        return False
    try:
        key.verify(bytes.fromhex(signature), canonical_json(body))
    except (InvalidSignature, ValueError):
        return False
    return True

def checkpoint_id(checkpoint: Mapping[str, Any]) -> str:
    return registry_digest({"body": dict(checkpoint["body"]), "signer_id": checkpoint["signer_id"], "signature": checkpoint["signature"]})

def compare_checkpoints(a: Mapping[str, Any], b: Mapping[str, Any], trusted_signers: Mapping[str, Ed25519PublicKey]) -> str:
    """Return SAME, ORDERED, FORK, or INCOMPARABLE after validating both signatures.

    ORDERED means the later checkpoint directly names the earlier checkpoint's
    checkpoint_id as its predecessor. It is not a general Merkle consistency proof.
    """
    if not verify_checkpoint(a, trusted_signers) or not verify_checkpoint(b, trusted_signers):
        raise ValueError("cannot compare invalid or untrusted checkpoints")
    x, y = a["body"], b["body"]
    if x["log_id"] != y["log_id"]:
        return "INCOMPARABLE"
    if x["size"] == y["size"]:
        return "SAME" if x["head_hash"] == y["head_hash"] else "FORK"
    earlier, later = (a, b) if x["size"] < y["size"] else (b, a)
    eb, lb = earlier["body"], later["body"]
    if lb["previous_checkpoint_hash"] == checkpoint_id(earlier):
        return "ORDERED"
    if eb["previous_checkpoint_hash"] == checkpoint_id(later):
        return "ORDERED"
    return "INCOMPARABLE"

