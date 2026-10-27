#!/usr/bin/env python3
"""CLXXXI model: release authorization requires two evidence classes and revision binding.

This is a policy truth-table regression. It does not execute repository modules
or verify the live producer, public key, status endpoint, or artifact attestation.
"""
from itertools import product


def authorize_safe(console_contract_ok, production_gates_ok, signature_ok, fresh, revision_artifact_bound):
    return all((console_contract_ok, production_gates_ok, signature_ok, fresh, revision_artifact_bound))


def authorize_unsafe(console_contract_ok, production_gates_ok, signature_ok, fresh, revision_artifact_bound):
    # Deliberate anti-pattern: signed, fresh console evidence is treated as release authority.
    del production_gates_ok, revision_artifact_bound
    return all((console_contract_ok, signature_ok, fresh))


def main():
    states = list(product((False, True), repeat=5))
    assert len(states) == 32

    counterexamples = [
        state for state in states
        if authorize_unsafe(*state) and not authorize_safe(*state)
    ]
    safe_invariant_violations = [
        state for state in states
        if authorize_safe(*state) and not all(state)
    ]

    assert counterexamples == [
        (True, False, True, True, False),
        (True, False, True, True, True),
        (True, True, True, True, False),
    ]
    assert safe_invariant_violations == []
    assert authorize_safe(True, True, True, True, True)
    assert not authorize_safe(False, True, True, True, True)
    assert not authorize_safe(True, False, True, True, True)
    assert not authorize_safe(True, True, False, True, True)
    assert not authorize_safe(True, True, True, False, True)
    assert not authorize_safe(True, True, True, True, False)

    print("CLXXXI two-source release-proof regression: PASS")
    print(f"truth-table states: {len(states)}")
    print(f"unsafe authorizations: {len(counterexamples)}")
    print(f"safe-policy invariant violations: {len(safe_invariant_violations)}")
    print("scope: model-only; repository and live release checks not executed")


if __name__ == "__main__":
    main()
