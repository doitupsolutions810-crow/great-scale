"""CXXXVI: exact finite optimization for constrained missing-unit classification.

Enumerates assignments of missing units to permitted strata, enforces stratum
count constraints, and optimizes the lower/upper population bounds. Intended as
a transparent reference solver for small instances and a correctness oracle for
future integer-programming implementations.
"""
from dataclasses import dataclass
from itertools import product
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
    lower_assignment: Tuple[str, ...]
    upper_assignment: Tuple[str, ...]
    feasible_assignments: int


def solve_exact(
    observed_sum: float,
    population: int,
    missing_units: Tuple[MissingUnit, ...],
    strata: dict[str, StratumRule],
) -> OptimizationResult:
    """Find the robust lower/upper endpoints over all feasible assignments."""
    if population <= 0:
        raise ValueError("population must be positive")
    if not isfinite(observed_sum):
        raise ValueError("observed_sum must be finite")
    if len(missing_units) > population:
        raise ValueError("missing units cannot exceed population")
    if not strata:
        raise ValueError("at least one stratum is required")
    for name, rule in strata.items():
        if not all(isfinite(x) for x in (rule.lower, rule.upper)):
            raise ValueError(f"support for {name} must be finite")
        if rule.lower > rule.upper:
            raise ValueError(f"invalid support for {name}")
        if rule.min_missing < 0 or (rule.max_missing is not None and rule.max_missing < rule.min_missing):
            raise ValueError(f"invalid count limits for {name}")
    choices = []
    for unit in missing_units:
        allowed = tuple(s for s in unit.allowed_strata if s in strata)
        if not allowed:
            raise ValueError("each missing unit must allow at least one known stratum")
        choices.append(allowed)

    candidates = []
    for assignment in product(*choices):
        counts = {name: 0 for name in strata}
        for name in assignment:
            counts[name] += 1
        if any(counts[name] < rule.min_missing or
               (rule.max_missing is not None and counts[name] > rule.max_missing)
               for name, rule in strata.items()):
            continue
        lower = (observed_sum + sum(counts[n] * rule.lower for n, rule in strata.items())) / population
        upper = (observed_sum + sum(counts[n] * rule.upper for n, rule in strata.items())) / population
        candidates.append((lower, upper, tuple(assignment)))
    if not candidates:
        raise ValueError("no feasible classification assignment")
    low = min(candidates, key=lambda x: x[0])
    high = max(candidates, key=lambda x: x[1])
    return OptimizationResult(low[0], high[1], low[2], high[2], len(candidates))
