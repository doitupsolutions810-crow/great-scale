#!/usr/bin/env python3
"""Exhaustive logical contract: accept evidence only with all three proof layers."""
from itertools import product


def accept(integrity: bool, authenticity: bool, execution: bool) -> bool:
    return integrity and authenticity and execution


def main() -> None:
    states = list(product((False, True), repeat=3))
    accepted = [state for state in states if accept(*state)]
    assert len(states) == 8
    assert accepted == [(True, True, True)]
    for state in states:
        assert accept(*state) is all(state)
    print("PASS evidence-triad contract: 8/8 states; accepted states=1")


if __name__ == "__main__":
    main()
