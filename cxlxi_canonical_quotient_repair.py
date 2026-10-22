"""CXLXI: canonical quotient repair after model updates."""
from __future__ import annotations
from collections import defaultdict
from typing import Hashable, Mapping, Sequence

State = Hashable
Block = frozenset[State]

def _validate(states, observations, properties, transitions):
    domain = set(states)
    if len(domain) != len(states):
        raise ValueError("states must be unique")
    if set(observations) != domain or set(properties) != domain or set(transitions) != domain:
        raise ValueError("observations, properties and transitions must cover exactly the state domain")
    for state, edges in transitions.items():
        if not isinstance(edges, Mapping):
            raise ValueError(f"transitions for {state!r} must be a mapping")
        for successor in edges.values():
            if successor is not None and successor not in domain:
                raise ValueError(f"successor {successor!r} is outside state domain")

def _sort_blocks(blocks):
    return sorted(blocks, key=lambda b: tuple(sorted(map(repr, b))))

def _bucket(states, key):
    buckets = defaultdict(list)
    for state in states:
        buckets[key(state)].append(state)
    return list(buckets.values())

def canonical_quotient(states, observations, properties, transitions) -> list[Block]:
    """Compute the coarsest stable partition preserving observations, properties and transitions."""
    _validate(states, observations, properties, transitions)
    blocks = _sort_blocks([frozenset(g) for g in _bucket(
        states, lambda s: (observations[s], tuple(properties[s])) )])
    while True:
        block_of = {s: i for i, block in enumerate(blocks) for s in block}
        def signature(s):
            edges = transitions[s]
            return (observations[s], tuple(properties[s]), frozenset(edges.keys()),
                    tuple(sorted(((repr(a), None if nxt is None else block_of[nxt])
                                  for a, nxt in edges.items()), key=lambda item: item[0])))
        refined = []
        for block in blocks:
            refined.extend(frozenset(g) for g in _bucket(list(block), signature))
        refined = _sort_blocks(refined)
        if frozenset(refined) == frozenset(blocks):
            return refined
        blocks = refined

def partition_signature(partition: Sequence[Sequence[State]]):
    return frozenset(frozenset(block) for block in partition)

def repair_and_audit(states, observations, properties, transitions,
                     cached_partition: Sequence[Sequence[State]]):
    current = canonical_quotient(states, observations, properties, transitions)
    cached = partition_signature(cached_partition)
    canonical = partition_signature(current)
    domain = set(states)
    cached_valid = ((set().union(*cached) == domain) if cached else not domain)
    cached_valid = cached_valid and sum(len(block) for block in cached) == len(domain)
    return {"canonical_partition": [sorted(map(repr, b)) for b in current],
            "cached_matches_canonical": cached_valid and cached == canonical,
            "cached_partition_valid_cover": cached_valid,
            "canonical_block_count": len(current), "cached_block_count": len(cached),
            "repair_needed": not (cached_valid and cached == canonical)}
