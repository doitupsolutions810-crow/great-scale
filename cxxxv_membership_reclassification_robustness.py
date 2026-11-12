"""CXXXV: robust partial-identification bounds under uncertain reclassification.

Each admissible classification scenario supplies per-stratum observed sums and
missing counts. For each scenario, unobserved values range over that stratum's
support. The returned interval is the union envelope over all admissible
scenarios. This is finite-scenario sensitivity analysis, not a probability model.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Tuple


@dataclass(frozen=True)
class Stratum:
    observed_sum: float
    missing_count: int
    lower: float
    upper: float


@dataclass(frozen=True)
class Scenario:
    name: str
    strata: Tuple[Stratum, ...]


@dataclass(frozen=True)
class Bounds:
    lower: float
    upper: float
    lower_scenario: str
    upper_scenario: str


def scenario_bounds(scenario: Scenario, population: int) -> tuple[float, float]:
    if population <= 0 or not scenario.strata:
        raise ValueError("population must be positive and scenario must have strata")
    observed = sum(s.observed_sum for s in scenario.strata)
    missing = 0
    for s in scenario.strata:
        if not all(isfinite(v) for v in (s.observed_sum, s.lower, s.upper)):
            raise ValueError("all numeric inputs must be finite")
        if isinstance(s.missing_count, bool) or not isinstance(s.missing_count, int) or s.missing_count < 0:
            raise ValueError("missing_count must be a nonnegative integer")
        if s.lower > s.upper:
            raise ValueError("lower support endpoint exceeds upper endpoint")
        missing += s.missing_count
    if missing > population:
        raise ValueError("missing count exceeds population")
    if not isfinite(observed):
        raise ValueError("observed sum must be finite")
    return (
        (observed + sum(s.missing_count * s.lower for s in scenario.strata)) / population,
        (observed + sum(s.missing_count * s.upper for s in scenario.strata)) / population,
    )


def robust_bounds(scenarios: Iterable[Scenario], population: int) -> Bounds:
    """Envelope all admissible scenarios; reject an empty scenario set."""
    candidates = [(sc.name, *scenario_bounds(sc, population)) for sc in scenarios]
    if not candidates:
        raise ValueError("at least one admissible scenario is required")
    lo = min(candidates, key=lambda item: item[1])
    hi = max(candidates, key=lambda item: item[2])
    return Bounds(lo[1], hi[2], lo[0], hi[0])
