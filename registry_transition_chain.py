"""CVIX: signed, hash-linked registry transitions with monotonic version checks."""
from __future__ import annotations
import hashlib
from typing import Any, Mapping
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from threshold_witness_checkpoint import canonical_json
from registry_provenance import registry_payload

TRANSITION_SCHEMA = "great-scale-registry-transition-v1"
GENESIS_PARENT = "0" * 64

def registry_digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(dict(payload))).hexdigest()

def create_transition(previous_registry: Mapping[str, Any] | None, next_version: int, next_domains: Mapping[str, str], authority_id: str, authority_key: Ed25519PrivateKey) -> dict[str, Any]:
    next_payload = registry_payload(next_version, next_domains)
    parent_hash = GENESIS_PARENT if previous_registry is None else registry_digest(previous_registry["payload"])
    if previous_registry is not None:
        old_version = previous_registry["payload"]["version"]
        if next_version != old_version + 1:
            raise ValueError("registry versions must advance exactly by one")
    body = {"schema": TRANSITION_SCHEMA, "parent_registry_hash": parent_hash, "registry_payload": next_payload, "registry_hash": registry_digest(next_payload)}
    return {"body": body, "authority_id": authority_id, "signature": authority_key.sign(canonical_json(body)).hex()}

def verify_transition(transition: Mapping[str, Any], previous_registry: Mapping[str, Any] | None, authority_keys: Mapping[str, Ed25519PublicKey]) -> bool:
    if not isinstance(transition, Mapping) or not isinstance(transition.get("body"), Mapping):
        raise ValueError("transition requires body")
    body = dict(transition["body"])
    payload = body.get("registry_payload")
    if body.get("schema") != TRANSITION_SCHEMA or not isinstance(payload, Mapping):
        return False
    try:
        canonical_payload = registry_payload(payload.get("version"), payload.get("witness_domains"))
    except (ValueError, TypeError, AttributeError):
        return False
    if dict(payload) != canonical_payload or body.get("registry_hash") != registry_digest(canonical_payload):
        return False
    expected_parent = GENESIS_PARENT if previous_registry is None else registry_digest(previous_registry["payload"])
    if body.get("parent_registry_hash") != expected_parent:
        return False
    expected_version = 1 if previous_registry is None else previous_registry["payload"]["version"] + 1
    if payload["version"] != expected_version:
        return False
    authority_id, signature = transition.get("authority_id"), transition.get("signature")
    key = authority_keys.get(authority_id) if isinstance(authority_id, str) else None
    if key is None or not isinstance(signature, str):
        return False
    try:
        key.verify(bytes.fromhex(signature), canonical_json(body))
    except (InvalidSignature, ValueError):
        return False
    return True

def apply_transition(transition: Mapping[str, Any], previous_registry: Mapping[str, Any] | None, authority_keys: Mapping[str, Ed25519PublicKey]) -> dict[str, Any]:
    if not verify_transition(transition, previous_registry, authority_keys):
        raise ValueError("registry transition invalid, stale, or out of sequence")
    return dict(transition["body"]["registry_payload"])

def verify_transition_chain(transitions: list[Mapping[str, Any]], authority_keys: Mapping[str, Ed25519PublicKey]) -> dict[str, Any] | None:
    current = None
    for transition in transitions:
        current = apply_transition(transition, current, authority_keys)
    return current
