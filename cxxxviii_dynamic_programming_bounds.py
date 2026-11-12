"""CXXXVIII: dynamic-programming solver for constrained classification bounds.

DP merges assignments that reach the same stratum-count state. This can be much
smaller than enumerating all unit-to-stratum assignments, though worst-case state
growth remains combinatorial. No third-party solver dependency is required.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Tuple


@dataclass(frozen=True)
class StratumRule:
    lower: float
    upper: float
    min_missing: int = 0
    max_missing: int | None = None


@dataclass(frozen=True)
class MissingUnit:
    allowed_strata: Tuple[str, ...]


@dataclass(frozen=True)
class OptimizationResult:
    lower: float
    upper: float
    lower_counts: Tuple[Tuple[str, int], ...]
    upper_counts: Tuple[Tuple[str, int], ...]
    feasible_count_vectors: int
    processed_states: int


def solve_dp(observed_sum: float, population: int, units: Tuple[MissingUnit, ...],
             strata: dict[str, StratumRule]) -> OptimizationResult:
    if population <= 0:
        raise ValueError("population must be positive")
    if not isfinite(observed_sum):
        raise ValueError("observed_sum must be finite")
    if len(units) > population:
        raise ValueError("missing units cannot exceed population")
    names = tuple(strata)
    if not names:
        raise ValueError("at least one stratum is required")
    for name, rule in strata.items():
        if not isfinite(rule.lower) or not isfinite(rule.upper) or rule.lower > rule.upper:
            raise ValueError(f"invalid support for {name}")
        if rule.min_missing < 0 or (rule.max_missing is not None and rule.max_missing < rule.min_missing):
            raise ValueError(f"invalid count limits for {name}")
    index = {name: i for i, name in enumerate(names)}
    maxes = tuple(min(len(units), strata[n].max_missing if strata[n].max_missing is not None else len(units)) for n in names)
    mins = tuple(strata[n].min_missing for n in names)
    # State maps count vectors to one representative assignment. Assignment
    # multiplicity is intentionally not counted; endpoints depend only on counts.
    states = {(0,) * len(names): ()}
    processed = 1
    for unit in units:
        allowed = tuple(dict.fromkeys(s for s in unit.allowed_strata if s in index))
        if not allowed:
            raise ValueError("each unit must allow at least one known stratum")
        next_states = {}
        for counts, assignment in states.items():
            for name in allowed:
                j = index[name]
                new = list(counts)
                new[j] += 1
                if new[j] > maxes[j]:
                    continue
                key = tuple(new)
                if key not in next_states:
                    next_states[key] = assignment + (name,)
        states = next_states
        processed += len(states)
        if not states:
            raise ValueError("no feasible classification assignment")
    feasible = [(counts, assignment) for counts, assignment in states.items()
                if all(counts[i] >= mins[i] for i in range(len(names)))]
    if not feasible:
        raise ValueError("no feasible classification assignment")
    def lower(row):
        counts, _ = row
        return (observed_sum + sum(counts[i] * strata[n].lower for i, n in enumerate(names))) / population
    def upper(row):
        counts, _ = row
        return (observed_sum + sum(counts[i] * strata[n].upper for i, n in enumerate(names))) / population
    low = min(feasible, key=lower)
    high = max(feasible, key=upper)
    return OptimizationResult(
        lower(low), upper(high),
        tuple(zip(names, low[0])), tuple(zip(names, high[0])),
        len(feasible), processed
    )
