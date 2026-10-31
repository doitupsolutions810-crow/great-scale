"""CXLV: finite-horizon behavioral equivalence and partition refinement."""
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, TypeVar

S = TypeVar("S", bound=Hashable)
A = TypeVar("A", bound=Hashable)
O = TypeVar("O", bound=Hashable)


@dataclass(frozen=True)
class HorizonAudit:
    horizon: int
    equivalent: bool
    first_distinguishing_depth: int | None
    reason: str | None


def compare_through_horizon(left, right, actions, transition, observation,
                            enabled=lambda _s, _a: True, horizon=1):
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    action_set = tuple(actions)
    def compare(x, y, depth):
        if observation(x) != observation(y):
            return HorizonAudit(depth, False, depth, "observation_mismatch")
        if depth == 0:
            return HorizonAudit(depth, True, None, None)
        for action in action_set:
            ex, ey = enabled(x, action), enabled(y, action)
            if ex != ey:
                return HorizonAudit(depth, False, depth, "enabled_action_mismatch")
            if not ex:
                continue
            nx, ny = transition(x, action), transition(y, action)
            if (nx is None) != (ny is None):
                return HorizonAudit(depth, False, depth, "terminal_mismatch")
            if nx is not None:
                child = compare(nx, ny, depth - 1)
                if not child.equivalent:
                    return HorizonAudit(depth, False, child.first_distinguishing_depth, child.reason)
        return HorizonAudit(depth, True, None, None)
    return compare(left, right, horizon)


def refine_behavioral_partition(states, actions, transition, observation,
                                enabled=lambda _s, _a: True):
    """Stable partition for a finite deterministic state/action domain."""
    domain, action_set = tuple(states), tuple(actions)
    blocks = []
    for state in domain:
        for block in blocks:
            if observation(block[0]) == observation(state):
                block.append(state)
                break
        else:
            blocks.append([state])
    while True:
        class_of = {state: i for i, block in enumerate(blocks) for state in block}
        signatures = {}
        for state in domain:
            transitions = []
            for action in action_set:
                if not enabled(state, action):
                    transitions.append((action, "disabled"))
                else:
                    nxt = transition(state, action)
                    transitions.append((action, "terminal") if nxt is None
                                       else (action, "next", class_of[nxt]))
            signatures.setdefault((observation(state), tuple(transitions)), []).append(state)
        refined = list(signatures.values())
        if {frozenset(x) for x in refined} == {frozenset(x) for x in blocks}:
            return tuple(tuple(x) for x in refined)
        blocks = refined
