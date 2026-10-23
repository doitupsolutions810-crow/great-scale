from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxviii_canonical_id_model import build_model, quotient_partition


def test_boolean_and_integer_observations_are_not_collapsed():
    model = build_model([
        {"label": "bool-observation", "observation": True, "properties": (), "transitions": []},
        {"label": "int-observation", "observation": 1, "properties": (), "transitions": []},
    ])
    partition = {frozenset(block) for block in quotient_partition(model)}
    assert len(partition) == 2


def test_boolean_and_integer_properties_are_not_collapsed():
    model = build_model([
        {"label": "bool-property", "observation": "same", "properties": (True,), "transitions": []},
        {"label": "int-property", "observation": "same", "properties": (1,), "transitions": []},
    ])
    partition = {frozenset(block) for block in quotient_partition(model)}
    assert len(partition) == 2


def test_typed_observation_keys_are_canonical_encoder_outputs():
    assert canonical_encode(True) != canonical_encode(1)
