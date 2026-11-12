"""CXLII: quantify compression against the coarsest outcome-preserving partition.

For a finite domain and a complete declared outcome signature, assignments
are equivalent exactly when their signatures match. This module compares a
candidate key's partition with that oracle partition.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, TypeVar

A = TypeVar("A")
K = TypeVar("K", bound=Hashable)
O = TypeVar("O", bound=Hashable)


@dataclass(frozen=True)
class PartitionReport:
    assignment_count: int
    candidate_state_count: int
    oracle_class_count: int
    sufficient: bool
    coarsest_for_signature: bool
    excess_states: int
    collisions: tuple[tuple[Hashable, object, object, Hashable, Hashable], ...]
    split_pairs: tuple[tuple[object, object, Hashable], ...]


def audit_partition(
    assignments: Iterable[A],
    state_key: Callable[[A], K],
    outcome: Callable[[A], O],
) -> PartitionReport:
    """Audit sufficiency and whether a key achieves the oracle's coarsest partition.

    A collision is an unsound merge: equal keys, unequal outcomes.
    A split pair is a redundant split: unequal keys, equal outcomes.
    """
    items = list(assignments)
    keys = [state_key(a) for a in items]
    outcomes = [outcome(a) for a in items]
    collisions = []
    split_pairs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if keys[i] == keys[j] and outcomes[i] != outcomes[j]:
                collisions.append((keys[i], items[i], items[j], outcomes[i], outcomes[j]))
            elif keys[i] != keys[j] and outcomes[i] == outcomes[j]:
                split_pairs.append((items[i], items[j], outcomes[i]))
    candidate_count = len(set(keys))
    oracle_count = len(set(outcomes))
    sufficient = not collisions
    # A sufficient key is coarsest exactly when it neither splits any
    # outcome-equivalent pair nor uses more groups than the outcome partition.
    coarsest = sufficient and not split_pairs and candidate_count == oracle_count
    return PartitionReport(
        assignment_count=len(items),
        candidate_state_count=candidate_count,
        oracle_class_count=oracle_count,
        sufficient=sufficient,
        coarsest_for_signature=coarsest,
        excess_states=candidate_count - oracle_count,
        collisions=tuple(collisions),
        split_pairs=tuple(split_pairs),
    )


def outcome_key(assignment: A, outcome: Callable[[A], O]) -> O:
    """Canonical coarsest key for the declared outcome signature."""
    return outcome(assignment)
