"""CXLIV: audit deterministic transition congruence over a finite domain."""
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, TypeVar

S = TypeVar("S", bound=Hashable)
A = TypeVar("A", bound=Hashable)
K = TypeVar("K", bound=Hashable)
O = TypeVar("O", bound=Hashable)


@dataclass(frozen=True)
class Witness:
    kind: str
    left_state: Hashable
    right_state: Hashable
    action: Hashable | None
    left_value: Hashable
    right_value: Hashable


@dataclass(frozen=True)
class TransitionAudit:
    states_checked: int
    equivalent_pairs_checked: int
    transition_comparisons: int
    violations: tuple[Witness, ...]

    @property
    def preserves_quotient(self) -> bool:
        return not self.violations


def audit_transition_congruence(
    states: Iterable[S],
    actions: Iterable[A],
    key: Callable[[S], K],
    transition: Callable[[S, A], S | None],
    observation: Callable[[S], O],
    enabled: Callable[[S, A], bool] = lambda _s, _a: True,
) -> TransitionAudit:
    """Check observation, action availability, terminal status, and successor keys.

    transition(s, a) returns None for a terminal/undefined transition. This is
    an exhaustive check only for the finite states/actions supplied by the caller.
    """
    domain, action_set = tuple(states), tuple(actions)
    violations: list[Witness] = []
    pairs = comparisons = 0
    for i, left in enumerate(domain):
        for right in domain[i + 1:]:
            if key(left) != key(right):
                continue
            pairs += 1
            if observation(left) != observation(right):
                violations.append(Witness("observation_collision", left, right, None,
                                          observation(left), observation(right)))
            for action in action_set:
                le, re = enabled(left, action), enabled(right, action)
                if le != re:
                    violations.append(Witness("enabled_action_mismatch", left, right,
                                              action, le, re))
                    continue
                if not le:
                    continue
                ln, rn = transition(left, action), transition(right, action)
                comparisons += 1
                if (ln is None) != (rn is None):
                    violations.append(Witness("terminal_mismatch", left, right, action,
                                              ln is None, rn is None))
                elif ln is not None and rn is not None and key(ln) != key(rn):
                    violations.append(Witness("successor_key_mismatch", left, right,
                                              action, key(ln), key(rn)))
    return TransitionAudit(len(domain), pairs, comparisons, tuple(violations))
