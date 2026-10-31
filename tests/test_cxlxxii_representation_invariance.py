from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxviii_canonical_id_model import TERMINAL, build_model, quotient_partition


def blocks_as_labels(model, partition):
    label_by_id = {canonical_encode(state["label"]): state["label"] for state in model["states"].values()}
    return {frozenset(label_by_id[sid] for sid in block) for block in partition}


def relabel_records(records, state_map, action_map):
    output = []
    for row in records:
        transitions = []
        for action, target in row["transitions"]:
            mapped_target = TERMINAL if target is TERMINAL else state_map[target]
            transitions.append((action_map[action], mapped_target))
        output.append({
            "label": state_map[row["label"]],
            "observation": row["observation"],
            "properties": row["properties"],
            "transitions": transitions,
        })
    return output


def test_quotient_partition_invariant_under_bijective_state_and_action_renaming():
    records = [
        {"label": "a", "observation": 0, "properties": ("x",), "transitions": [("go", "b")]},
        {"label": "b", "observation": 0, "properties": ("x",), "transitions": [("go", TERMINAL)]},
        {"label": "c", "observation": 1, "properties": ("y",), "transitions": [("go", "b")]},
    ]
    state_map = {"a": "state-z", "b": "state-x", "c": "state-y"}
    action_map = {"go": "action-renamed"}
    renamed = relabel_records(records, state_map, action_map)

    original_model = build_model(records)
    renamed_model = build_model(renamed)
    original_blocks = blocks_as_labels(original_model, quotient_partition(original_model))
    renamed_blocks = blocks_as_labels(renamed_model, quotient_partition(renamed_model))
    expected_renamed = {frozenset(state_map[label] for label in block) for block in original_blocks}
    assert renamed_blocks == expected_renamed


def test_state_renaming_does_not_change_number_or_membership_pattern_of_blocks():
    records = [
        {"label": "p", "observation": True, "properties": (), "transitions": [("step", "q")]},
        {"label": "q", "observation": True, "properties": (), "transitions": [("step", TERMINAL)]},
        {"label": "r", "observation": 1, "properties": (), "transitions": []},
    ]
    state_map = {"p": "omega", "q": "alpha", "r": "delta"}
    renamed = relabel_records(records, state_map, {"step": "move"})
    model_a, model_b = build_model(records), build_model(renamed)
    blocks_a = blocks_as_labels(model_a, quotient_partition(model_a))
    blocks_b = blocks_as_labels(model_b, quotient_partition(model_b))
    assert blocks_b == {frozenset(state_map[x] for x in block) for block in blocks_a}
