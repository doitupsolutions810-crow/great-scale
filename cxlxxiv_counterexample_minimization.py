"""Deterministic delta-debugging for finite sequence-shaped counterexamples."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")


def minimize_counterexample(
    case: Sequence[T],
    still_fails: Callable[[tuple[T, ...]], bool],
) -> tuple[T, ...]:
    """Return a 1-minimal subsequence that still fails.

    The predicate must be deterministic and return True exactly when the
    failure is reproduced. The result is 1-minimal: removing any single
    remaining element makes the predicate false. It is not guaranteed to be
    globally shortest, and it preserves order while removing elements.
    """
    current = tuple(case)
    if not still_fails(current):
        raise ValueError("initial case does not reproduce the failure")

    granularity = 2
    while len(current) >= 2:
        chunk_size = (len(current) + granularity - 1) // granularity
        reduced = False
        for start in range(0, len(current), chunk_size):
            candidate = current[:start] + current[start + chunk_size :]
            if candidate and still_fails(candidate):
                current = candidate
                granularity = max(2, granularity - 1)
                reduced = True
                break
        if reduced:
            continue
        if granularity >= len(current):
            break
        granularity = min(len(current), granularity * 2)

    # Verify the promised local minimality instead of relying only on the loop.
    for index in range(len(current)):
        candidate = current[:index] + current[index + 1 :]
        if candidate and still_fails(candidate):
            raise AssertionError("minimizer did not reach 1-minimal result")
    return current
