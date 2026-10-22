"""CXLX: robustness of behavioral/property quotients under model change.

A conservative reference implementation: seed refinement from a previous
partition where possible, split by current observations/properties, then refine
until enabled actions and successor blocks are congruent. The full recomputation
is retained as an independent oracle for validation.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Hashable, Mapping, Sequence

State = Hashable
Action = Hashable
Block = frozenset[State]


def _validate(states, observations, properties, transitions):
    state_set = set(states)
    if len(state_set) != len(states):
        raise ValueError("states must be unique")
    if set(observations) != state_set:
        raise ValueError("observations must cover exactly the state domain")
    if set(properties) != state_set:
        raise ValueError("properties must cover exactly the state domain")
    if set(transitions) != state_set:
        raise ValueError("transitions must cover exactly the state domain")
    for state, edges in transitions.items():
        if not isinstance(edges, Mapping):
            raise ValueError(f"transitions for {state!r} must be a mapping")
        for action, successor in edges.items():
            if successor is not None and successor not in state_set:
                raise ValueError(f"successor {successor!r} from {state!r} is outside state domain")


def _canonical_partition(groups: Sequence[Sequence[State]], states: Sequence[State]) -> list[Block]:
    domain = set(states)
    seen = set()
    result = []
    for group in groups:
        block = frozenset(group)
        if not block:
            continue
        if not block <= domain or seen.intersection(block):
            raise ValueError("partition has out-of-domain or duplicate states")
        seen.update(block)
        result.append(block)
    if seen != domain:
        raise ValueError("partition must cover every state exactly once")
    return sorted(result, key=lambda b: tuple(sorted(map(repr, b))))


def _refine(states, observations, properties, transitions, seed):
    blocks = _canonical_partition(seed, states)
    # Existing distinctions are preserved; current observable/property
    # signatures can only split a prior block, never merge its members.
    def split_by(groups, key):
        out = []
        for group in groups:
            buckets = defaultdict(list)
            for s in group:
                buckets[key(s)].append(s)
            out.extend(frozenset(v) for v in buckets.values())
        return sorted(out, key=lambda b: tuple(sorted(map(repr, b))))

    blocks = split_by(blocks, lambda s: (observations[s], tuple(properties[s])))
    while True:
        block_of = {s: i for i, block in enumerate(blocks) for s in block}
        def signature(s):
            edges = transitions[s]
            return (
                observations[s],
                tuple(properties[s]),
                frozenset(edges.keys()),
                tuple(sorted(
                    ((repr(a), None if nxt is None else block_of[nxt])
                     for a, nxt in edges.items()),
                    key=lambda pair: pair[0],
                )),
            )
        new_blocks = split_by(blocks, signature)
        if new_blocks == blocks:
            return blocks
        blocks = new_blocks


def full_recompute(states, observations, properties, transitions) -> list[Block]:
    """Compute the coarsest quotient preserving observations, properties and transitions."""
    _validate(states, observations, properties, transitions)
    # Start with one block; initial signature splits it by present observables.
    return _refine(states, observations, properties, transitions, [list(states)] if states else [])


def incremental_refine(states, observations, properties, transitions,
                       previous_partition: Sequence[Sequence[State]]) -> list[Block]:
    """Refine a prior partition for a changed model; conservatively retain old distinctions."""
    _validate(states, observations, properties, transitions)
    current = set(states)
    surviving = []
    covered = set()
    for old_block in previous_partition:
        members = [s for s in old_block if s in current and s not in covered]
        if members:
            surviving.append(members)
            covered.update(members)
    # Newly introduced states begin as singleton blocks: no unsupported merge
    # with an old state is assumed without a separate equivalence proof.
    surviving.extend([[s] for s in states if s not in covered])
    return _refine(states, observations, properties, transitions, surviving)


def partition_signature(partition: Sequence[Sequence[State]]) -> frozenset[frozenset[State]]:
    """Order-independent representation for comparing partitions."""
    return frozenset(frozenset(block) for block in partition)


def audit_incremental_against_full(states, observations, properties, transitions,
                                   previous_partition):
    """Return a deterministic comparison report for incremental vs full recomputation."""
    incremental = incremental_refine(states, observations, properties, transitions, previous_partition)
    full = full_recompute(states, observations, properties, transitions)
    same = partition_signature(incremental) == partition_signature(full)
    return {
        "incremental_partition": [sorted(map(repr, b)) for b in incremental],
        "full_partition": [sorted(map(repr, b)) for b in full],
        "equivalent": same,
        "incremental_block_count": len(incremental),
        "full_block_count": len(full),
        "preserves_old_distinctions": True,
    }
