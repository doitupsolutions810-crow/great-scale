import pytest

from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxii_quotient_certificate import make_certificate, verify_certificate


def test_encoder_distinguishes_bool_and_int():
    assert canonical_encode(True) != canonical_encode(1)


def test_model_rejects_python_equal_but_canonically_distinct_states():
    states = [True, 1]
    # Ordinary Python dicts cannot represent these as separate keys.
    observations = {True: "same"}
    properties = {True: ()}
    transitions = {True: {}}
    with pytest.raises(ValueError, match="Python equality/hash collision"):
        make_certificate(states, observations, properties, transitions, [{True}, {1}])


def test_distinct_representable_labels_make_valid_certificate():
    states = [1, "1"]
    observations = {1: 0, "1": 0}
    properties = {1: (), "1": ()}
    transitions = {1: {}, "1": {}}
    partition = [{1}, {"1"}]
    cert = make_certificate(states, observations, properties, transitions, partition)
    assert len(cert["state_to_block"]) == 2
    assert verify_certificate(states, observations, properties, transitions, partition, cert)["valid"]


def test_equality_collision_is_rejected_before_domain_map_check():
    # This specifically guards against set(states) silently collapsing True and 1.
    with pytest.raises(ValueError, match="Python equality/hash collision"):
        make_certificate([True, 1], {}, {}, {}, [])
