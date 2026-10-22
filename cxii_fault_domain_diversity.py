"""CXII: fault-domain-aware independent witness coverage."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cxi_independent_witness_gossip import verify_observation

def analyze_fault_domains(
    receipts: Sequence[Mapping[str, Any]],
    trusted_observers: Mapping[str, Ed25519PublicKey],
    trusted_log_signers: Mapping[str, Ed25519PublicKey],
    observer_domains: Mapping[str, str],
    minimum_observers: int = 3,
    minimum_domains: int = 2,
) -> dict[str, Any]:
    """Count verified unique observers and declared domains; detect same-size forks.

    Domain labels are trusted configuration metadata, not cryptographic proof
    that operators or infrastructure are actually independent.
    """
    for name, value in (("minimum_observers", minimum_observers), ("minimum_domains", minimum_domains)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    accepted: dict[str, Mapping[str, Any]] = {}
    rejected = 0
    duplicates: set[str] = set()
    for receipt in receipts:
        if not verify_observation(receipt, trusted_observers, trusted_log_signers):
            rejected += 1
            continue
        observer = receipt["body"]["observer_id"]
        if observer in accepted:
            duplicates.add(observer)
            continue
        accepted[observer] = receipt["body"]["checkpoint"]
    missing_domain = sorted(o for o in accepted if not observer_domains.get(o, "").strip())
    domain_set = {observer_domains[o] for o in accepted if o not in missing_domain}
    buckets: dict[tuple[str, int], set[str]] = {}
    for cp in accepted.values():
        b = cp["body"]
        buckets.setdefault((b["log_id"], b["size"]), set()).add(b["head_hash"])
    conflicts = [{"log_id": log_id, "size": size, "head_hashes": sorted(heads)}
                 for (log_id, size), heads in sorted(buckets.items()) if len(heads) > 1]
    enough_observers = len(accepted) >= minimum_observers
    enough_domains = len(domain_set) >= minimum_domains and not missing_domain
    if conflicts:
        status = "FORK_DETECTED"
    elif enough_observers and enough_domains:
        status = "DIVERSITY_THRESHOLD_MET"
    else:
        status = "INSUFFICIENT_DIVERSITY"
    return {
        "status": status,
        "verified_observer_count": len(accepted),
        "declared_domain_count": len(domain_set),
        "minimum_observers": minimum_observers,
        "minimum_domains": minimum_domains,
        "observer_threshold_met": enough_observers,
        "domain_threshold_met": enough_domains,
        "observers_missing_domain": missing_domain,
        "duplicate_observer_ids": sorted(duplicates),
        "rejected_receipts": rejected,
        "conflicts": conflicts,
        "scope_note": "Domain diversity is based on configured labels. It does not prove independence of ownership, software, network, upstream data, or administration."
    }
