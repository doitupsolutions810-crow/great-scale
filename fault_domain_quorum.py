"""CVII: fault-domain-aware quorum verification for Great Scale checkpoints."""
from __future__ import annotations
from typing import Any, Mapping
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from threshold_witness_checkpoint import canonical_json, checkpoint_statement

def verify_fault_diverse_checkpoint(
    checkpoint: Mapping[str, Any],
    trace: Any,
    public_keys: Mapping[str, Ed25519PublicKey],
    witness_domains: Mapping[str, str],
    threshold: int,
    min_domains: int,
    expected_sequence: int,
    expected_previous_anchor: str | None = None,
) -> bool:
    """Accept only if k trusted signatures and d distinct configured fault domains verify.

    The domain map is an operator-supplied trust assumption, not cryptographic proof
    that infrastructure or ownership is actually independent.
    """
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError("threshold must be a positive integer")
    if isinstance(min_domains, bool) or not isinstance(min_domains, int) or min_domains < 1:
        raise ValueError("min_domains must be a positive integer")
    if threshold > len(public_keys):
        raise ValueError("threshold cannot exceed the trusted witness registry")
    if min_domains > threshold:
        raise ValueError("min_domains cannot exceed signature threshold")
    if set(public_keys) - set(witness_domains):
        raise ValueError("every trusted witness must have a configured fault domain")
    if any(not isinstance(witness_domains[w], str) or not witness_domains[w].strip() for w in public_keys):
        raise ValueError("fault domains must be non-empty strings")
    if not isinstance(checkpoint, Mapping):
        raise ValueError("checkpoint must be a mapping")
    statement, signatures = checkpoint.get("statement"), checkpoint.get("signatures")
    if not isinstance(statement, Mapping) or not isinstance(signatures, list):
        raise ValueError("checkpoint requires statement and signatures list")
    expected = checkpoint_statement(trace, expected_sequence, expected_previous_anchor)
    if dict(statement) != expected:
        return False
    seen, valid_ids = set(), set()
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
        valid_ids.add(wid)
    domains = {witness_domains[wid] for wid in valid_ids}
    return len(valid_ids) >= threshold and len(domains) >= min_domains
