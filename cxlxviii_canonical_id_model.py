"""Canonical-ID model representation that avoids Python label-key collisions."""
from __future__ import annotations
from collections import defaultdict
from collections.abc import Iterable, Mapping
from cxlxiv_canonical_typed_encoding import canonical_encode


class ModelError(ValueError):
    """Raised when a model record is ambiguous or unsupported."""


def build_model(records: Iterable[Mapping]):
    """Normalize sequence-based records using canonical IDs as primary keys.

    Each record has label, observation, properties, and transitions. Transitions
    are a sequence of (action_label, successor_label) pairs, not a dict keyed
    by user labels, so True and 1 can coexist.
    """
    rows = list(records)
    states = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ModelError("each state record must be a mapping")
        for key in ("label", "observation", "properties", "transitions"):
            if key not in row:
                raise ModelError(f"missing state field: {key}")
        sid = canonical_encode(row["label"])
        if sid in states:
            raise ModelError("duplicate canonical state identity")
        states[sid] = {
            "label": row["label"],
            "observation": row["observation"],
            "properties": tuple(row["properties"]),
            "transitions": {},
        }

    for row in rows:
        sid = canonical_encode(row["label"])
        seen_actions = set()
        for edge in row["transitions"]:
            if not isinstance(edge, (tuple, list)) or len(edge) != 2:
                raise ModelError("each transition must be an (action, successor) pair")
            action, successor_label = edge
            aid = canonical_encode(action)
            if aid in seen_actions:
                raise ModelError("duplicate canonical action identity within state")
            seen_actions.add(aid)
            if successor_label is None:
                successor_id = None
            else:
                successor_id = canonical_encode(successor_label)
                if successor_id not in states:
                    raise ModelError("successor outside state domain")
            states[sid]["transitions"][aid] = successor_id
    return {"schema": "gs-canonical-id-model-v1", "states": states}


def quotient_partition(model):
    """Return the coarsest deterministic behavioral/property partition as ID sets."""
    if model.get("schema") != "gs-canonical-id-model-v1":
        raise ModelError("unsupported model schema")
    states = model.get("states")
    if not isinstance(states, Mapping):
        raise ModelError("states must be a mapping")
    groups = defaultdict(set)
    for sid, state in states.items():
        groups[(state["observation"], state["properties"])].add(sid)
    partition = list(groups.values())
    while True:
        block_of = {sid: i for i, block in enumerate(partition) for sid in block}
        next_partition = []
        for block in partition:
            buckets = defaultdict(set)
            for sid in block:
                edges = states[sid]["transitions"]
                signature = tuple(sorted(
                    (aid, None if target is None else block_of[target])
                    for aid, target in edges.items()
                ))
                buckets[signature].add(sid)
            next_partition.extend(buckets.values())
        if {frozenset(b) for b in next_partition} == {frozenset(b) for b in partition}:
            return tuple(frozenset(b) for b in next_partition)
        partition = next_partition


def validate_model(model):
    """Check primary-key and transition integrity; return True or raise ModelError."""
    if model.get("schema") != "gs-canonical-id-model-v1":
        raise ModelError("unsupported model schema")
    states = model.get("states")
    if not isinstance(states, Mapping):
        raise ModelError("states must be a mapping")
    for sid, state in states.items():
        if sid != canonical_encode(state["label"]):
            raise ModelError("state key does not match canonical label identity")
        edges = state.get("transitions")
        if not isinstance(edges, Mapping):
            raise ModelError("transitions must be keyed by canonical action IDs")
        for aid, target in edges.items():
            if not isinstance(aid, str):
                raise ModelError("action IDs must be canonical strings")
            if target is not None and target not in states:
                raise ModelError("successor outside state domain")
    return True
