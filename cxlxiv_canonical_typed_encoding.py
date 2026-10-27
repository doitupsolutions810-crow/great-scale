"""CXLXIV: deterministic typed encoding for supported state/action labels."""
from __future__ import annotations
import json
import math
from typing import Any

class UnsupportedLabel(TypeError):
    pass

def canonical_value(value: Any):
    """Return a type-tagged JSON-compatible value; unsupported types fail closed."""
    t=type(value)
    if value is None: return ["none"]
    if t is bool: return ["bool", value]
    if t is int: return ["int", str(value)]
    if t is str: return ["str", value]
    if t is float:
        if not math.isfinite(value): raise UnsupportedLabel("non-finite floats are not supported")
        return ["float64", value.hex()]
    if t is tuple: return ["tuple", [canonical_value(v) for v in value]]
    raise UnsupportedLabel(f"unsupported label type: {t.__module__}.{t.__qualname__}")

def canonical_encode(value: Any) -> str:
    """Stable UTF-8-ready encoding for supported primitive/tuple labels."""
    return json.dumps(canonical_value(value), ensure_ascii=False, separators=(",", ":"))

def validate_unique_labels(values):
    encoded={}
    for value in values:
        key=canonical_encode(value)
        if key in encoded and type(encoded[key]) is not type(value):
            raise ValueError("canonical encoding collision")
        encoded[key]=value
    return tuple(encoded.keys())

def encode_model(states, transitions):
    """Encode state and action identities and reject duplicate encoded identities."""
    state_ids=[canonical_encode(s) for s in states]
    if len(set(state_ids)) != len(state_ids): raise ValueError("duplicate canonical state identity")
    action_ids=[]
    for state in states:
        if state not in transitions: raise ValueError("transition map missing state")
        for action in transitions[state]: action_ids.append(canonical_encode(action))
    # Repeated labels across states are valid; canonical encodings must be injective
    # over distinct typed values, which canonical_encode provides for supported types.
    return {"state_ids":state_ids,"action_ids":sorted(set(action_ids)),"encoding_version":"gs-typed-v1"}
