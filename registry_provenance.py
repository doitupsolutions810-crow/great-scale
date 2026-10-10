"""CVIII: versioned, signed witness-domain registry provenance."""
from __future__ import annotations
import hashlib
from typing import Any, Mapping
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from threshold_witness_checkpoint import canonical_json, trace_commitment, sign_statement

REGISTRY_SCHEMA = "great-scale-witness-registry-v1"
CHECKPOINT_SCHEMA = "great-scale-registry-bound-checkpoint-v1"

def registry_payload(version: int, witness_domains: Mapping[str, str]) -> dict[str, Any]:
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError("registry version must be a positive integer")
    if not witness_domains:
        raise ValueError("registry must contain at least one witness")
    clean = {}
    for wid, domain in witness_domains.items():
        if not isinstance(wid, str) or not wid.strip():
            raise ValueError("witness IDs must be non-empty strings")
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("fault domains must be non-empty strings")
        clean[wid] = domain
    return {"schema": REGISTRY_SCHEMA, "version": version, "witness_domains": dict(sorted(clean.items()))}

def create_signed_registry(version: int, witness_domains: Mapping[str, str], authority_id: str, authority_key: Ed25519PrivateKey) -> dict[str, Any]:
    if not isinstance(authority_id, str) or not authority_id.strip():
        raise ValueError("authority_id must be a non-empty string")
    payload = registry_payload(version, witness_domains)
    digest = hashlib.sha256(canonical_json(payload)).hexdigest()
    signature = authority_key.sign(canonical_json(payload)).hex()
    return {"payload": payload, "registry_hash": digest, "authority_id": authority_id, "signature": signature}

def verify_signed_registry(registry: Mapping[str, Any], authority_keys: Mapping[str, Ed25519PublicKey]) -> bool:
    if not isinstance(registry, Mapping) or not isinstance(registry.get("payload"), Mapping):
        raise ValueError("registry requires payload")
    payload = dict(registry["payload"])
    try:
        expected = registry_payload(payload.get("version"), payload.get("witness_domains"))
    except (ValueError, TypeError, AttributeError):
        return False
    if payload != expected:
        return False
    digest = hashlib.sha256(canonical_json(payload)).hexdigest()
    if registry.get("registry_hash") != digest:
        return False
    authority_id, signature = registry.get("authority_id"), registry.get("signature")
    key = authority_keys.get(authority_id) if isinstance(authority_id, str) else None
    if key is None or not isinstance(signature, str):
        return False
    try:
        key.verify(bytes.fromhex(signature), canonical_json(payload))
    except (InvalidSignature, ValueError):
        return False
    return True

def create_registry_bound_checkpoint(trace: Any, sequence: int, previous_anchor: str | None, registry: Mapping[str, Any], witnesses: Mapping[str, Ed25519PrivateKey]) -> dict[str, Any]:
    payload = registry.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("registry requires payload")
    digest = hashlib.sha256(canonical_json(dict(payload))).hexdigest()
    if registry.get("registry_hash") != digest:
        raise ValueError("registry hash does not match payload")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
        raise ValueError("sequence must be a non-negative integer")
    statement = {"schema": CHECKPOINT_SCHEMA, "sequence": sequence, "previous_anchor": previous_anchor, "trace_commitment": trace_commitment(trace), "registry_version": payload.get("version"), "registry_hash": digest}
    signatures = [sign_statement(statement, wid, key) for wid, key in sorted(witnesses.items())]
    return {"statement": statement, "signatures": signatures}

def verify_registry_bound_checkpoint(checkpoint: Mapping[str, Any], trace: Any, registry: Mapping[str, Any], authority_keys: Mapping[str, Ed25519PublicKey], witness_keys: Mapping[str, Ed25519PublicKey], threshold: int, expected_sequence: int, expected_previous_anchor: str | None = None, required_registry_version: int | None = None) -> bool:
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError("threshold must be a positive integer")
    if threshold > len(witness_keys):
        raise ValueError("threshold cannot exceed trusted witness registry")
    if not verify_signed_registry(registry, authority_keys):
        return False
    registry_payload_value = registry["payload"]
    if required_registry_version is not None and registry_payload_value["version"] != required_registry_version:
        return False
    digest = hashlib.sha256(canonical_json(dict(registry_payload_value))).hexdigest()
    expected = {"schema": CHECKPOINT_SCHEMA, "sequence": expected_sequence, "previous_anchor": expected_previous_anchor, "trace_commitment": trace_commitment(trace), "registry_version": registry_payload_value["version"], "registry_hash": digest}
    statement, signatures = checkpoint.get("statement"), checkpoint.get("signatures")
    if not isinstance(statement, Mapping) or not isinstance(signatures, list) or dict(statement) != expected:
        return False
    seen, valid = set(), 0
    payload = canonical_json(dict(statement))
    for item in signatures:
        if not isinstance(item, Mapping):
            raise ValueError("signature entries must be mappings")
        wid, sig = item.get("witness_id"), item.get("signature")
        if not isinstance(wid, str) or not wid:
            raise ValueError("invalid witness ID")
        if wid in seen:
            raise ValueError(f"duplicate witness identity: {wid}")
        seen.add(wid)
        key = witness_keys.get(wid)
        if key is None or wid not in registry_payload_value["witness_domains"] or not isinstance(sig, str):
            continue
        try:
            key.verify(bytes.fromhex(sig), payload)
        except (InvalidSignature, ValueError):
            continue
        valid += 1
    return valid >= threshold
