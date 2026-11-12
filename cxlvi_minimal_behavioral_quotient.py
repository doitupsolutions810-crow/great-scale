"""CXLVI: build and audit the coarsest stable behavioral quotient for finite deterministic systems."""
from dataclasses import dataclass


@dataclass(frozen=True)
class QuotientResult:
    blocks: tuple[tuple[object, ...], ...]
    initial_state_count: int
    quotient_state_count: int
    reductions: int
    stable: bool


def minimal_behavioral_quotient(states, actions, transition, observation,
                                enabled=lambda _s, _a: True):
    """Refine observation classes until transition signatures stabilize.

    Assumes every non-None successor belongs to the supplied finite state domain.
    """
    domain, action_set = tuple(states), tuple(actions)
    if len(set(domain)) != len(domain):
        raise ValueError("states must be unique")
    domain_set = set(domain)
    for state in domain:
        for action in action_set:
            if enabled(state, action):
                nxt = transition(state, action)
                if nxt is not None and nxt not in domain_set:
                    raise ValueError("transition successor is outside supplied state domain")

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
            edges = []
            for action in action_set:
                if not enabled(state, action):
                    edges.append((action, "disabled"))
                else:
                    nxt = transition(state, action)
                    edges.append((action, "terminal") if nxt is None
                                 else (action, "next", class_of[nxt]))
            signatures.setdefault((observation(state), tuple(edges)), []).append(state)
        refined = list(signatures.values())
        old = {frozenset(block) for block in blocks}
        new = {frozenset(block) for block in refined}
        blocks = refined
        if old == new:
            break

    result_blocks = tuple(tuple(block) for block in blocks)
    return QuotientResult(result_blocks, len(domain), len(result_blocks),
                          len(domain) - len(result_blocks), True)


def verify_quotient(result, actions, transition, observation,
                    enabled=lambda _s, _a: True):
    """Independently check observation, enabled-action and successor-block consistency."""
    class_of = {state: i for i, block in enumerate(result.blocks) for state in block}
    action_set = tuple(actions)
    for block in result.blocks:
        for left in block:
            for right in block:
                if observation(left) != observation(right):
                    return False
                for action in action_set:
                    le, re = enabled(left, action), enabled(right, action)
                    if le != re:
                        return False
                    if not le:
                        continue
                    ln, rn = transition(left, action), transition(right, action)
                    if (ln is None) != (rn is None):
                        return False
                    if ln is not None and class_of[ln] != class_of[rn]:
                        return False
    return True
