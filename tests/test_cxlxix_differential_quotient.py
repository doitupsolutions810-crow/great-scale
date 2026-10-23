from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxviii_canonical_id_model import TERMINAL, build_model, quotient_partition, validate_model


def test_none_is_state_label_distinct_from_terminal_marker():
    model = build_model([
        {"label": None, "observation": "none-state", "properties": (), "transitions": []},
        {"label": "source", "observation": "source", "properties": (), "transitions": [("go", None)]},
        {"label": "terminal-source", "observation": "terminal-source", "properties": (), "transitions": [("stop", TERMINAL)]},
    ])
    assert canonical_encode(None) in model["states"]
    assert model["states"][canonical_encode("source")]["transitions"][canonical_encode("go")] == canonical_encode(None)
    assert model["states"][canonical_encode("terminal-source")]["transitions"][canonical_encode("stop")] is None
    assert validate_model(model)


def test_differential_refinement_partition_matches_reference():
    model = build_model([
        {"label": "a", "observation": 0, "properties": (), "transitions": [("go", "b")]},
        {"label": "b", "observation": 0, "properties": (), "transitions": [("go", TERMINAL)]},
        {"label": "c", "observation": 1, "properties": (), "transitions": [("go", "b")]},
    ])
    states = model["states"]
    got = {frozenset(block) for block in quotient_partition(model)}
    groups = {}
    for sid, state in states.items():
        groups.setdefault((state["observation"], state["properties"]), set()).add(sid)
    ref = list(groups.values())
    while True:
        idx = {sid: i for i, block in enumerate(ref) for sid in block}
        next_ref = []
        for block in ref:
            buckets = {}
            for sid in block:
                edges = states[sid]["transitions"]
                signature = tuple(sorted((aid, None if target is None else idx[target]) for aid, target in edges.items()))
                buckets.setdefault(signature, set()).add(sid)
            next_ref.extend(buckets.values())
        if {frozenset(x) for x in next_ref} == {frozenset(x) for x in ref}:
            expected = {frozenset(x) for x in next_ref}
            break
        ref = next_ref
    assert got == expected
