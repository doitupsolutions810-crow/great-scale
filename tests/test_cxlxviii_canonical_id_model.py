import pytest

from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxviii_canonical_id_model import ModelError, build_model, quotient_partition, validate_model


def test_bool_and_int_can_coexist_as_distinct_primary_ids():
    model = build_model([
        {"label": True, "observation": "bool", "properties": (), "transitions": [("next", 1)]},
        {"label": 1, "observation": "int", "properties": (), "transitions": [("next", True)]},
    ])
    assert len(model["states"]) == 2
    assert canonical_encode(True) in model["states"]
    assert canonical_encode(1) in model["states"]
    assert validate_model(model)


def test_edges_resolve_to_canonical_successor_ids():
    model = build_model([
        {"label": True, "observation": "a", "properties": (), "transitions": [("next", 1)]},
        {"label": 1, "observation": "b", "properties": (), "transitions": []},
    ])
    assert model["states"][canonical_encode(True)]["transitions"][canonical_encode("next")] == canonical_encode(1)


def test_unknown_successor_fails_closed():
    with pytest.raises(ModelError, match="successor outside"):
        build_model([{"label": "x", "observation": 0, "properties": (), "transitions": [("go", "missing")]}])


def test_duplicate_canonical_state_id_rejected():
    with pytest.raises(ModelError, match="duplicate canonical"):
        build_model([
            {"label": 1, "observation": 0, "properties": (), "transitions": []},
            {"label": 1, "observation": 1, "properties": (), "transitions": []},
        ])


def test_quotient_preserves_observations_and_properties():
    model = build_model([
        {"label": True, "observation": 0, "properties": (), "transitions": []},
        {"label": 1, "observation": 1, "properties": (), "transitions": []},
        {"label": "one", "observation": 0, "properties": (), "transitions": []},
    ])
    partition = quotient_partition(model)
    assert len(partition) == 2
    assert validate_model(model)
