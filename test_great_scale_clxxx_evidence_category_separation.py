#!/usr/bin/env python3
"""CLXXX regression model: console self-checks must not impersonate production gates.

This is a formal policy model. It does not fetch or execute the Control Plane or
Lattice Ops source, and it is not a substitute for cross-repository integration tests.
"""
from itertools import product


def authorize_safe(console_contract_ok, production_gates_ok, signature_ok, fresh, schema_ok):
    return all((console_contract_ok, production_gates_ok, signature_ok, fresh, schema_ok))


def authorize_unsafe(console_contract_ok, production_gates_ok, signature_ok, fresh, schema_ok):
    # Deliberate anti-pattern: accepts E-series console evidence but silently omits G-series.
    del production_gates_ok
    return all((console_contract_ok, signature_ok, fresh, schema_ok))


def main():
    states = list(product((False, True), repeat=5))
    assert len(states) == 32, "truth table must exhaust all five Boolean predicates"

    counterexamples = []
    safe_invariant_violations = []
    for e_ok, g_ok, signature_ok, fresh, schema_ok in states:
        safe = authorize_safe(e_ok, g_ok, signature_ok, fresh, schema_ok)
        unsafe = authorize_unsafe(e_ok, g_ok, signature_ok, fresh, schema_ok)
        if unsafe and not safe:
            counterexamples.append((e_ok, g_ok, signature_ok, fresh, schema_ok))
        if safe and not all((e_ok, g_ok, signature_ok, fresh, schema_ok)):
            safe_invariant_violations.append((e_ok, g_ok, signature_ok, fresh, schema_ok))

    assert counterexamples == [(True, False, True, True, True)], (
        "must find exactly the E-pass/G-fail category-confusion counterexample"
    )
    assert safe_invariant_violations == [], "safe authorization must require every predicate"
    assert authorize_safe(True, True, True, True, True) is True
    assert authorize_safe(True, False, True, True, True) is False
    assert authorize_safe(True, True, False, True, True) is False
    assert authorize_safe(True, True, True, False, True) is False
    assert authorize_safe(True, True, True, True, False) is False

    print("CLXXX formal policy regression: PASS")
    print(f"truth-table states: {len(states)}")
    print(f"unsafe category-confusion counterexamples: {len(counterexamples)}")
    print(f"safe-policy invariant violations: {len(safe_invariant_violations)}")
    print("scope: model-only; no repository or live deployment execution")


if __name__ == "__main__":
    main()
