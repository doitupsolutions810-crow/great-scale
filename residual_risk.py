"""Great Scale LXXXVI: finite-model residual risk calculations."""
from itertools import combinations
from math import prod
from typing import Mapping, Iterable


def surviving_paths(path_dependencies: Mapping[str, Iterable[str]], failed_sources: Iterable[str]) -> list[str]:
    failed = set(failed_sources)
    return sorted(path for path, deps in path_dependencies.items() if not (set(deps) & failed))


def state_probability(failure_probabilities: Mapping[str, float], failed_sources: Iterable[str]) -> float:
    failed = set(failed_sources)
    if not failed <= set(failure_probabilities):
        raise ValueError("failed_sources contains an unknown source")
    for source, p in failure_probabilities.items():
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"probability for {source!r} must be in [0, 1]")
    return prod(p if source in failed else 1.0 - p for source, p in failure_probabilities.items())


def modeled_reliability(path_dependencies: Mapping[str, Iterable[str]], failure_probabilities: Mapping[str, float], required_paths: int) -> float:
    """Exact reliability by enumerating all source-failure states (2**m)."""
    if required_paths < 0:
        raise ValueError("required_paths must be non-negative")
    sources = sorted(failure_probabilities)
    if any(not set(deps) <= set(sources) for deps in path_dependencies.values()):
        raise ValueError("every dependency must have a supplied failure probability")
    total = 0.0
    for size in range(len(sources) + 1):
        for state in combinations(sources, size):
            if len(surviving_paths(path_dependencies, state)) >= required_paths:
                total += state_probability(failure_probabilities, state)
    return min(1.0, max(0.0, total))


def interval_reliability_bounds(path_dependencies: Mapping[str, Iterable[str]], probability_intervals: Mapping[str, tuple[float, float]], required_paths: int) -> tuple[float, float]:
    """Reliability bounds for independent failures and a fixed dependency map."""
    lows, highs = {}, {}
    for source, interval in probability_intervals.items():
        if len(interval) != 2:
            raise ValueError("each interval must be (lower, upper)")
        low, high = interval
        if not (0 <= low <= high <= 1):
            raise ValueError(f"invalid probability interval for {source!r}")
        lows[source], highs[source] = low, high
    return (modeled_reliability(path_dependencies, highs, required_paths),
            modeled_reliability(path_dependencies, lows, required_paths))


def incompleteness_adjusted_bounds(modeled_probability: float, eta: float) -> tuple[float, float]:
    """Mixture bounds when unmodeled scenario mass q is between 0 and eta."""
    if not 0 <= modeled_probability <= 1:
        raise ValueError("modeled_probability must be in [0, 1]")
    if not 0 <= eta <= 1:
        raise ValueError("eta must be in [0, 1]")
    return ((1.0 - eta) * modeled_probability,
            (1.0 - eta) * modeled_probability + eta)
