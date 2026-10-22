"""CXLVII: audit whether state properties survive quotient compression."""
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Iterable, TypeVar

S = TypeVar("S", bound=Hashable)


@dataclass(frozen=True)
class PropertyConflict(Generic[S]):
    block_index: int
    left_state: S
    right_state: S
    left_value: bool
    right_value: bool


@dataclass(frozen=True)
class PropertyAudit(Generic[S]):
    preserved: bool
    quotient_values: tuple[bool | None, ...]
    conflicts: tuple[PropertyConflict[S], ...]

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)


def audit_state_property(blocks: Iterable[Iterable[S]],
                         property_fn: Callable[[S], bool]) -> PropertyAudit[S]:
    """A Boolean property survives iff it is constant on every quotient block."""
    values: list[bool | None] = []
    conflicts: list[PropertyConflict[S]] = []
    for i, items in enumerate(blocks):
        block = tuple(items)
        if not block:
            raise ValueError(f"quotient block {i} is empty")
        first = bool(property_fn(block[0]))
        values.append(first)
        for state in block[1:]:
            value = bool(property_fn(state))
            if value != first:
                conflicts.append(PropertyConflict(i, block[0], state, first, value))
    bad_blocks = {c.block_index for c in conflicts}
    quotient_values = tuple(None if i in bad_blocks else v for i, v in enumerate(values))
    return PropertyAudit(not conflicts, quotient_values, tuple(conflicts))


def property_on_quotient(blocks: Iterable[Iterable[S]],
                         property_fn: Callable[[S], bool]) -> tuple[bool, ...]:
    """Induce a property on quotient blocks, or raise with a counterexample."""
    materialized = tuple(tuple(block) for block in blocks)
    audit = audit_state_property(materialized, property_fn)
    if not audit.preserved:
        c = audit.conflicts[0]
        raise ValueError(
            "property is not quotient-invariant: "
            f"block {c.block_index} contains {c.left_state!r} -> {c.left_value} and "
            f"{c.right_state!r} -> {c.right_value}"
        )
    return tuple(bool(v) for v in audit.quotient_values)
