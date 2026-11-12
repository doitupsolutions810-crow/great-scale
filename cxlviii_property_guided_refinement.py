"""CXLVIII — refine quotient blocks until requested Boolean properties are constant."""
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, TypeVar

S = TypeVar("S", bound=Hashable)
Property = Callable[[S], bool]


@dataclass(frozen=True)
class RefinementReport:
    blocks: tuple[tuple[Hashable, ...], ...]
    initial_block_count: int
    final_block_count: int
    split_count: int
    properties_preserved: bool


def refine_partition_by_properties(
    blocks: Iterable[Iterable[S]],
    properties: Iterable[Property[S]],
) -> RefinementReport:
    """Split, never merge, each block by the joint signature of requested properties.

    Empty blocks and duplicate states are rejected so that each input state has
    one unambiguous location. This routine preserves the input partition's
    distinctions; it does not independently establish transition congruence.
    """
    partition = tuple(tuple(block) for block in blocks)
    if any(not block for block in partition):
        raise ValueError("partition contains an empty block")
    flattened = [state for block in partition for state in block]
    if len(set(flattened)) != len(flattened):
        raise ValueError("a state appears more than once in the partition")
    funcs = tuple(properties)
    refined: list[tuple[S, ...]] = []
    for block in partition:
        buckets: dict[tuple[bool, ...], list[S]] = {}
        for state in block:
            signature = tuple(bool(fn(state)) for fn in funcs)
            buckets.setdefault(signature, []).append(state)
        refined.extend(tuple(bucket) for bucket in buckets.values())
    # Check every requested property is constant on each resulting block.
    preserved = all(
        len({bool(fn(s)) for s in block}) <= 1
        for block in refined for fn in funcs
    )
    return RefinementReport(
        blocks=tuple(refined),
        initial_block_count=len(partition),
        final_block_count=len(refined),
        split_count=len(refined) - len(partition),
        properties_preserved=preserved,
    )
