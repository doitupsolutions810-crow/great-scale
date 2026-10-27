"""Regression tests for stable terminal identity and typed quotient semantics."""
from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxviii_canonical_id_model import TERMINAL, build_model, quotient_partition


def _blocks(model):
    return {frozenset(block) for block in quotient_partition(model)}


def test_terminal_marker_is_one_stable_module_level_sentinel():
    model = build_model([
        {"label": "a", "observation": "x", "properties": (), "transitions": [("finish", TERMINAL)]},
        {"label": "b", "observation": "x", "properties": (), "transitions": [("finish", TERMINAL)]},
    ])
    assert len(model["states"]) == 2
    assert len(_blocks(model)) == 1


def test_none_state_label_is_distinct_from_terminal_marker():
    model = build_model([
        {"label": None, "observation": "x", "properties": (), "transitions": []},
        {"label": "a", "observation": "x", "properties": (), "transitions": [("finish", TERMINAL)]},
    ])
    assert canonical_encode(None) in model["states"]
    assert len(model["states"]) == 2


def test_boolean_and_integer_observations_remain_distinct():
    model = build_model([
        {"label": "bool", "observation": True, "properties": (), "transitions": []},
        {"label": "int", "observation": 1, "properties": (), "transitions": []},
    ])
    assert len(_blocks(model)) == 2
