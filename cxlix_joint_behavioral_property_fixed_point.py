"""CXLIX — compute a stable quotient preserving observations, transitions, properties."""
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Mapping, TypeVar

S = TypeVar("S", bound=Hashable)
Action = Hashable
Property = Callable[[S], bool]


@dataclass(frozen=True)
class FixedPointReport:
    blocks: tuple[tuple[Hashable, ...], ...]
    iterations: int
    initial_block_count: int
    final_block_count: int
    stable: bool
    properties_preserved: bool
    transition_consistent: bool


def joint_refinement(
    states: Iterable[S],
    transitions: Mapping[S, Mapping[Action, S]],
    observations: Mapping[S, Hashable],
    properties: Iterable[Property[S]],
) -> FixedPointReport:
    """Refine to a deterministic observation/property-respecting bisimulation partition.

    transitions[state] maps each enabled action to its successor. Missing actions
    are disabled. Every successor must be in states. Terminal states have no
    enabled actions. The result is a fixed point under signatures containing
    observation, property values, enabled actions, and successor block IDs.
    """
    state_list = tuple(states)
    if len(set(state_list)) != len(state_list):
        raise ValueError("states must be unique")
    state_set = set(state_list)
    if set(transitions) != state_set or set(observations) != state_set:
        raise ValueError("transitions and observations must cover exactly all states")
    for state, edges in transitions.items():
        for action, successor in edges.items():
            if successor not in state_set:
                raise ValueError(f"successor {successor!r} from {state!r} is outside states")
    props = tuple(properties)

    def initial_signature(s: S):
        return (observations[s], tuple(bool(p(s)) for p in props))

    def group_by(signatures):
        buckets = {}
        for s in state_list:
            buckets.setdefault(signatures[s], []).append(s)
        return tuple(tuple(bucket) for bucket in buckets.values())

    blocks = group_by({s: initial_signature(s) for s in state_list})
    initial_block_count = len(blocks)
    iterations = 0
    while True:
        block_id = {s: i for i, block in enumerate(blocks) for s in block}
        signatures = {}
        for s in state_list:
            edge_signature = tuple(sorted(
                ((repr(action), block_id[target]) for action, target in transitions[s].items()),
                key=lambda item: item[0],
            ))
            signatures[s] = (
                initial_signature(s),
                tuple(sorted(repr(a) for a in transitions[s])),
                edge_signature,
            )
        refined = group_by(signatures)
        iterations += 1
        if refined == blocks:
            break
        # Guard monotonicity explicitly: every new block must be a subset of one old block.
        old_owner = {s: i for i, block in enumerate(blocks) for s in block}
        if any(len({old_owner[s] for s in block}) != 1 for block in refined):
            raise AssertionError("refinement attempted to merge prior blocks")
        blocks = refined

    final_id = {s: i for i, block in enumerate(blocks) for s in block}
    prop_ok = all(len({bool(p(s)) for s in block}) <= 1 for block in blocks for p in props)
    transition_ok = True
    for block in blocks:
        representative = block[0]
        for s in block[1:]:
            if observations[s] != observations[representative]:
                transition_ok = False
            if set(transitions[s]) != set(transitions[representative]):
                transition_ok = False
            else:
                for action in transitions[s]:
                    if final_id[transitions[s][action]] != final_id[transitions[representative][action]]:
                        transition_ok = False
    return FixedPointReport(
        blocks=blocks,
        iterations=iterations,
        initial_block_count=initial_block_count,
        final_block_count=len(blocks),
        stable=True,
        properties_preserved=prop_ok,
        transition_consistent=transition_ok,
    )
