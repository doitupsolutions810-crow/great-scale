#!/usr/bin/env python3
"""Finite-state contract test for production startup readiness.

This models the required implication; it does not replace integration tests of
the actual service startup path.
"""
from itertools import product


def production_ready(production, key_valid, policy_valid, identity_attested):
    if not production:
        return True  # lab mode is explicitly outside the production guarantee
    return key_valid and policy_valid and identity_attested


def main():
    checked = 0
    for production, key_valid, policy_valid, identity_attested in product((False, True), repeat=4):
        ready = production_ready(production, key_valid, policy_valid, identity_attested)
        if production:
            expected = key_valid and policy_valid and identity_attested
            assert ready is expected, (production, key_valid, policy_valid, identity_attested, ready)
        else:
            assert ready is True
        checked += 1
    assert checked == 16
    print(f"PASS startup-readiness contract: {checked}/16 states")


if __name__ == "__main__":
    main()
