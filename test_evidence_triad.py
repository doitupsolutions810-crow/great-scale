#!/usr/bin/env python3
"""Exhaustive logical contract for integrity, authenticity, execution, and authority."""
from itertools import product


def accept(integrity: bool, authenticity: bool, execution: bool, authority: bool) -> bool:
    return integrity and authenticity and execution and authority


def main() -> None:
    states = list(product((False, True), repeat=4))
    accepted = [state for state in states if accept(*state)]
    assert len(states) == 16
    assert accepted == [(True, True, True, True)]
    for state in states:
        assert accept(*state) is all(state)

    # Each proof obligation is independently necessary.
    all_true = (True, True, True, True)
    for index in range(4):
        invalid = list(all_true)
        invalid[index] = False
        assert not accept(*invalid)

    # A correctly authenticated and executed artifact is still not authorized
    # for a caller who lacks access to the selected resource.
    assert not accept(True, True, True, False)
    print("PASS four-gate evidence contract: 16/16 states; accepted states=1")


if __name__ == "__main__":
    main()
