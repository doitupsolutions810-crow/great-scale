#!/usr/bin/env python3
"""CLXXXII: release authorization needs policy predicates plus observable exact-head proof."""
from itertools import product


def authorize(evidence_contract, production_gates, signature, freshness, revision_binding, observable_exact_head_ci):
    return all((evidence_contract, production_gates, signature, freshness, revision_binding, observable_exact_head_ci))


def main():
    states = list(product((False, True), repeat=6))
    assert len(states) == 64
    authorized = [state for state in states if authorize(*state)]
    assert authorized == [(True, True, True, True, True, True)]

    names = ("contract", "production_gates", "signature", "freshness", "revision_binding", "observable_exact_head_ci")
    for index, name in enumerate(names):
        state = [True] * 6
        state[index] = False
        assert not authorize(*state), f"missing {name} must deny release"

    assert not authorize(True, True, True, True, True, False)
    assert not authorize(True, False, True, True, True, True)
    print("CLXXXII proof-carrying release model: PASS")
    print(f"truth-table states: {len(states)}")
    print(f"authorized states: {len(authorized)}")
    print("single-predicate denial cases: 6/6")
    print("scope: model-only; no repository integration or live deployment executed")


if __name__ == "__main__":
    main()
