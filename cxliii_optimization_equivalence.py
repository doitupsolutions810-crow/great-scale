"""CXLIII: finite-domain audit of optimization-preserving compression."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, TypeVar

A = TypeVar("A")
K = TypeVar("K", bound=Hashable)


@dataclass(frozen=True)
class OptimizationReport:
    assignment_count: int
    feasible_count: int
    compressed_state_count: int
    feasible_state_count: int
    feasible_set_preserved: bool
    objective_preserved: bool
    optimum_preserved: bool
    original_optimum: float | None
    compressed_optimum: float | None
    collision_witnesses: tuple[tuple[object, object], ...]


def audit_optimization_compression(
    assignments: Iterable[A],
    state_key: Callable[[A], K],
    feasible: Callable[[A], bool],
    objective: Callable[[A], float],
) -> OptimizationReport:
    """Check whether a key preserves feasibility and the minimum objective.

    Compression represents each key by one state. It is safe for the declared
    optimization problem only if every key group is feasibility-homogeneous
    and, among feasible members, objective-homogeneous. This conservative
    criterion preserves the feasible set's state-level meaning, not just one
    coincidentally equal optimum.
    """
    items = list(assignments)
    groups: dict[K, list[A]] = {}
    for a in items:
        groups.setdefault(state_key(a), []).append(a)

    collisions = []
    for members in groups.values():
        first = members[0]
        for other in members[1:]:
            if feasible(first) != feasible(other):
                collisions.append((first, other))
            elif feasible(first) and objective(first) != objective(other):
                collisions.append((first, other))

    feasible_items = [a for a in items if feasible(a)]
    original_optimum = min((objective(a) for a in feasible_items), default=None)
    compressed_feasible_objectives = []
    for members in groups.values():
        feasible_members = [a for a in members if feasible(a)]
        if feasible_members:
            # Use the representative objective only if the group is homogeneous;
            # when it is not, collision witnesses already make the audit fail.
            compressed_feasible_objectives.append(objective(feasible_members[0]))
    compressed_optimum = min(compressed_feasible_objectives, default=None)

    feasible_set_preserved = not any(
        feasible(a) != feasible(b)
        for members in groups.values()
        for i, a in enumerate(members)
        for b in members[i + 1:]
    )
    objective_preserved = not any(
        feasible(a) and feasible(b) and objective(a) != objective(b)
        for members in groups.values()
        for i, a in enumerate(members)
        for b in members[i + 1:]
    )
    optimum_preserved = original_optimum == compressed_optimum
    return OptimizationReport(
        assignment_count=len(items),
        feasible_count=len(feasible_items),
        compressed_state_count=len(groups),
        feasible_state_count=sum(any(feasible(a) for a in g) for g in groups.values()),
        feasible_set_preserved=feasible_set_preserved,
        objective_preserved=objective_preserved,
        optimum_preserved=optimum_preserved,
        original_optimum=original_optimum,
        compressed_optimum=compressed_optimum,
        collision_witnesses=tuple(collisions),
    )
