"""CXLI: finite-model audit of proposed compressed states.

The audit checks whether assignments merged by a proposed state key agree on
all supplied downstream observables (feasibility and objective signature).
It is exhaustive for the finite assignment list provided; it does not prove
sufficiency for models or assignments not represented in that list.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, TypeVar

A = TypeVar("A")
K = TypeVar("K", bound=Hashable)
S = TypeVar("S", bound=Hashable)


@dataclass(frozen=True)
class Collision:
    state_key: Hashable
    first_assignment: object
    second_assignment: object
    first_signature: Hashable
    second_signature: Hashable


@dataclass(frozen=True)
class SufficiencyReport:
    assignment_count: int
    compressed_state_count: int
    sufficient: bool
    collisions: tuple[Collision, ...]


def audit_state_sufficiency(
    assignments: Iterable[A],
    state_key: Callable[[A], K],
    outcome_signature: Callable[[A], S],
) -> SufficiencyReport:
    """Find assignments collapsed to the same key but with different outcomes.

    The outcome signature must include every downstream distinction relevant
    to the intended task (for example, feasibility plus objective/cost vector).
    """
    groups: dict[K, list[tuple[A, S]]] = defaultdict(list)
    total = 0
    for assignment in assignments:
        total += 1
        groups[state_key(assignment)].append(
            (assignment, outcome_signature(assignment))
        )

    collisions: list[Collision] = []
    for key, members in groups.items():
        if not members:
            continue
        first_assignment, first_signature = members[0]
        for other_assignment, other_signature in members[1:]:
            if other_signature != first_signature:
                collisions.append(Collision(
                    state_key=key,
                    first_assignment=first_assignment,
                    second_assignment=other_assignment,
                    first_signature=first_signature,
                    second_signature=other_signature,
                ))
                break
    return SufficiencyReport(
        assignment_count=total,
        compressed_state_count=len(groups),
        sufficient=not collisions,
        collisions=tuple(collisions),
    )


def adaptive_key(
    assignment: tuple[str, ...],
    unit_effects: tuple[dict[str, tuple[float, float]], ...],
) -> tuple[tuple[tuple[str, int], ...], float, float]:
    """Example refined key: category counts plus accumulated lower/upper sums."""
    counts: dict[str, int] = {}
    lower = upper = 0.0
    for unit, category in enumerate(assignment):
        counts[category] = counts.get(category, 0) + 1
        lo, hi = unit_effects[unit][category]
        lower += lo
        upper += hi
    return tuple(sorted(counts.items())), round(lower, 12), round(upper, 12)
