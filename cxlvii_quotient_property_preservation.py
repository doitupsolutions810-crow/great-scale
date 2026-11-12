"""CXLVII: audit whether a state property survives quotienting."""
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Mapping, TypeVar

State = TypeVar("State", bound=Hashable)
Value = TypeVar("Value")


@dataclass(frozen=True)
class PropertyWitness:
    block_index: int
    left_state: Hashable
    right_state: Hashable
    left_value: object
    right_value: object


@dataclass(frozen=True)
class PropertyAudit:
    preserved: bool
    block_count: int
    checked_state_count: int
    witnesses: tuple[PropertyWitness, ...]

    @property
    def witness_count(self) -> int:
        return len(self.witnesses)


def audit_state_property(
    blocks: Iterable[Iterable[State]],
    property_fn: Callable[[State], Value],
) -> PropertyAudit:
    """Find blocks where the supplied property is not constant."""
    materialized = [tuple(block) for block in blocks]
    if any(not block for block in materialized):
        raise ValueError("quotient blocks must be non-empty")

    seen: set[State] = set()
    witnesses: list[PropertyWitness] = []
    checked = 0
    for index, block in enumerate(materialized):
        for state in block:
            if state in seen:
                raise ValueError("each state must occur in exactly one block")
            seen.add(state)
        checked += len(block)
        first = block[0]
        first_value = property_fn(first)
        for state in block[1:]:
            value = property_fn(state)
            if value != first_value:
                witnesses.append(PropertyWitness(index, first, state, first_value, value))
    return PropertyAudit(not witnesses, len(materialized), checked, tuple(witnesses))


def property_on_quotient(
    blocks: Iterable[Iterable[State]],
    property_fn: Callable[[State], Value],
) -> Mapping[State, tuple[int, Value]]:
    """Return state -> (class index, property value); reject mixed classes."""
    materialized = [tuple(block) for block in blocks]
    audit = audit_state_property(materialized, property_fn)
    if not audit.preserved:
        witness = audit.witnesses[0]
        raise ValueError(
            "property is not quotient-invariant: "
            f"{witness.left_state!r} -> {witness.left_value!r}, "
            f"{witness.right_state!r} -> {witness.right_value!r}"
        )
    result: dict[State, tuple[int, Value]] = {}
    for index, block in enumerate(materialized):
        value = property_fn(block[0])
        for state in block:
            result[state] = (index, value)
    return result
