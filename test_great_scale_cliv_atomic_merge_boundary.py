#!/usr/bin/env python3
"""CLIV: a client-side final read is not an atomic merge precondition."""
from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    head: str
    base: str
    workflow: str
    candidate: str


def merge_is_safe(state_at_read: State, tested_state: State,
                  server_enforced_authorization: bool) -> bool:
    # Equality is necessary but does not close the TOCTOU interval.
    return (
        state_at_read == tested_state
        and server_enforced_authorization
    )


def test_matching_read_without_server_guard_is_not_sufficient():
    tested = State("H1", "B1", "W1", "M1")
    assert tested == tested
    assert not merge_is_safe(tested, tested, False)


def test_server_guard_and_matching_candidate_are_required():
    tested = State("H1", "B1", "W1", "M1")
    assert merge_is_safe(tested, tested, True)


def test_state_movement_rejects_even_if_server_flag_is_true():
    tested = State("H1", "B1", "W1", "M1")
    moved = State("H1", "B2", "W1", "M2")
    assert not merge_is_safe(moved, tested, True)


if __name__ == "__main__":
    tests = [
        test_matching_read_without_server_guard_is_not_sufficient,
        test_server_guard_and_matching_candidate_are_required,
        test_state_movement_rejects_even_if_server_flag_is_true,
    ]
    for test in tests:
        test()
    print(f"PASS CLIV: atomic merge-boundary contract ({len(tests)}/{len(tests)} tests)")
