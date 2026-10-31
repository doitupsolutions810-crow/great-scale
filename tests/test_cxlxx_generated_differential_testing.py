from itertools import product

from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxviii_canonical_id_model import TERMINAL, build_model, quotient_partition


def reference_partition(model):
    states = model["states"]
    groups = {}
    for sid, state in states.items():
        groups.setdefault((state["observation"], state["properties"]), set()).add(sid)
    partition = list(groups.values())
    while True:
        block_of = {sid: i for i, block in enumerate(partition) for sid in block}
        refined = []
        for block in partition:
            buckets = {}
            for sid in block:
                edges = states[sid]["transitions"]
                signature = tuple(sorted(
                    (aid, None if target is None else block_of[target])
                    for aid, target in edges.items()
                ))
                buckets.setdefault(signature, set()).add(sid)
            refined.extend(buckets.values())
        if {frozenset(x) for x in refined} == {frozenset(x) for x in partition}:
            return {frozenset(x) for x in refined}
        partition = refined


def make_records(obs_bits, targets):
    labels = ["s0", "s1", "s2"]
    records = []
    for i, label in enumerate(labels):
        target = targets[i]
        transitions = [] if target == -2 else [("go", TERMINAL if target == -1 else labels[target])]
        records.append({
            "label": label,
            "observation": obs_bits[i],
            "properties": (),
            "transitions": transitions,
        })
    return records


def test_generated_three_state_models_match_reference_refinement():
    # Exhaust all binary observations and each state's absent/terminal/s0/s1/s2 edge.
    # 2^3 * 5^3 = 1000 deterministic finite models.
    labels = ["s0", "s1", "s2"]
    cases = 0
    for obs in product((0, 1), repeat=3):
        for targets in product((-2, -1, 0, 1, 2), repeat=3):
            # Keep scope bounded while including absent edges and terminal edges.
            records = []
            for i, label in enumerate(labels):
                target = targets[i]
                edges = [] if target == -2 else [("go", TERMINAL if target == -1 else labels[target])]
                records.append({"label": label, "observation": obs[i], "properties": (), "transitions": edges})
            model = build_model(records)
            got = {frozenset(block) for block in quotient_partition(model)}
            expected = reference_partition(model)
            assert got == expected, {"obs": obs, "targets": targets, "got": got, "expected": expected}
            cases += 1
    assert cases == 1000


def test_typed_identity_collision_labels_remain_distinct():
    model = build_model([
        {"label": True, "observation": 0, "properties": (), "transitions": [("next", 1)]},
        {"label": 1, "observation": 1, "properties": (), "transitions": [("next", TERMINAL)]},
    ])
    assert canonical_encode(True) in model["states"]
    assert canonical_encode(1) in model["states"]
    assert len(model["states"]) == 2
