#!/usr/bin/env python3
"""CLXXXVI: gate namespaces require contract proof and observed fallback state."""
from itertools import product

DEGRADED = {"not_found", "unreachable", "unconfigured", "invalid"}


def authorize(status, authority, trust_verified, local_opt_in, cone_ok):
    public_ok = (
        status == "ok"
        and authority == "public"
        and trust_verified is True
    )
    local_fallback_observed = status in DEGRADED
    evidence_authorized = (
        public_ok
        or (
            authority == "local"
            and local_fallback_observed
            and local_opt_in is True
        )
    )
    return evidence_authorized and cone_ok


def main():
    statuses = ["ok", "not_found", "unreachable", "unconfigured", "invalid", None, "mystery"]
    authorities = ["public", "local", "unknown"]
    states = list(product(statuses, authorities, (False, True), (False, True), (False, True)))
    assert len(states) == 168
    authorized = 0
    for status, authority, trust, opt_in, cone in states:
        result = authorize(status, authority, trust, opt_in, cone)
        if result:
            authorized += 1
            assert cone
            assert (
                (status == "ok" and authority == "public" and trust is True)
                or (authority == "local" and status in DEGRADED and opt_in is True)
            )

    assert authorize("ok", "public", True, False, True)
    assert not authorize("ok", "public", False, False, True)
    assert not authorize(None, "local", False, True, True)
    assert not authorize("mystery", "local", False, True, True)
    assert authorize("unreachable", "local", False, True, True)
    assert not authorize("unreachable", "local", False, False, True)
    assert not authorize("ok", "public", True, False, False)
    print("CLXXXVI gate namespace contract-binding model: PASS")
    print(f"truth-table states: {len(states)}")
    print(f"authorizing states: {authorized}")
    print("status-only public authority: denied")
    print("missing/unknown local status: denied")
    print("explicit opt-in + recognized degraded state: required")
    print("cone violation: denied")
    print("scope: policy model only; JavaScript repository suite remains unverified")


if __name__ == "__main__":
    main()
