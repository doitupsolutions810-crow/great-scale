"""Fault-diversity analysis for robust evidence replication.

This finite dependency model is an engineering diagnostic, not a proof that a
real-world dependency inventory is complete.
"""
from itertools import combinations
from typing import Iterable, Mapping


def surviving_paths(
    path_dependencies: Mapping[str, Iterable[str]],
    failed_sources: Iterable[str],
) -> tuple[str, ...]:
    """Return pathways with no declared dependency in failed_sources."""
    failed = set(failed_sources)
    return tuple(sorted(
        path for path, deps in path_dependencies.items()
        if not (set(deps) & failed)
    ))


def conclusion_supported(
    path_dependencies: Mapping[str, Iterable[str]],
    failed_sources: Iterable[str],
    required_paths: int,
) -> bool:
    """Whether at least required_paths survive the specified failures."""
    if required_paths < 1:
        raise ValueError("required_paths must be at least 1")
    if required_paths > len(path_dependencies):
        raise ValueError("required_paths exceeds the number of pathways")
    return len(surviving_paths(path_dependencies, failed_sources)) >= required_paths


def minimal_cut_sets(
    path_dependencies: Mapping[str, Iterable[str]],
    required_paths: int,
    candidate_sources: Iterable[str] | None = None,
) -> tuple[tuple[str, ...], ...]:
    """Enumerate minimal source-failure sets that defeat the required threshold.

    This is exponential in the number of candidate sources and intended for
    small audit models. A cut set is minimal if no proper subset also defeats
    the threshold.
    """
    if required_paths < 1 or required_paths > len(path_dependencies):
        raise ValueError("required_paths must be between 1 and pathway count")
    if candidate_sources is None:
        sources = sorted({source for deps in path_dependencies.values() for source in deps})
    else:
        sources = sorted(set(candidate_sources))
    cuts: list[tuple[str, ...]] = []
    for size in range(1, len(sources) + 1):
        for candidate in combinations(sources, size):
            candidate_set = set(candidate)
            if any(set(cut).issubset(candidate_set) for cut in cuts):
                continue
            if not conclusion_supported(path_dependencies, candidate, required_paths):
                cuts.append(candidate)
    return tuple(cuts)
