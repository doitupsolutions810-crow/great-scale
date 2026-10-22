"""Great Scale CXXXII: sharp population bounds from justified stratum supports.

The guarantee is conditional: each stratum's support limits must be externally
defensible and must contain every possible missing outcome in that stratum.
"""
from dataclasses import dataclass
from math import isclose
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Stratum:
    population: int
    observed_values: tuple[float, ...]
    lower: float
    upper: float

    @property
    def missing(self) -> int:
        return self.population - len(self.observed_values)

    @property
    def observed_sum(self) -> float:
        return sum(self.observed_values)


@dataclass(frozen=True)
class Bounds:
    lower: float
    upper: float

    @property
    def width(self) -> float:
        return self.upper - self.lower


def _validate(strata: Sequence[Stratum]) -> None:
    if not strata:
        raise ValueError("at least one stratum is required")
    for s in strata:
        if s.population < 1 or len(s.observed_values) > s.population:
            raise ValueError("invalid population or observed count")
        if not (s.lower <= s.upper):
            raise ValueError("lower support must not exceed upper support")
        if any(not (s.lower <= x <= s.upper) for x in s.observed_values):
            raise ValueError("observed value falls outside its declared stratum support")


def stratified_bounds(strata: Sequence[Stratum]) -> Bounds:
    """Sharp mean bounds under valid, stratum-specific support restrictions."""
    _validate(strata)
    total = sum(s.population for s in strata)
    lo = sum(s.observed_sum + s.missing * s.lower for s in strata) / total
    hi = sum(s.observed_sum + s.missing * s.upper for s in strata) / total
    return Bounds(lo, hi)


def global_support_bounds(strata: Sequence[Stratum], lower: float, upper: float) -> Bounds:
    """Comparator using one common support interval for every missing unit."""
    _validate(strata)
    if lower > upper:
        raise ValueError("lower support must not exceed upper support")
    total = sum(s.population for s in strata)
    observed_sum = sum(s.observed_sum for s in strata)
    missing = sum(s.missing for s in strata)
    if any(x < lower or x > upper for s in strata for x in s.observed_values):
        raise ValueError("observed value falls outside global support")
    return Bounds((observed_sum + missing * lower) / total,
                  (observed_sum + missing * upper) / total)


def endpoints_are_attainable(strata: Sequence[Stratum]) -> bool:
    """Check endpoint construction algebraically via missing-value assignments."""
    b = stratified_bounds(strata)
    total = sum(s.population for s in strata)
    low_sum = high_sum = 0.0
    for s in strata:
        low_sum += s.observed_sum + s.missing * s.lower
        high_sum += s.observed_sum + s.missing * s.upper
    return isclose(low_sum / total, b.lower) and isclose(high_sum / total, b.upper)


def demo() -> dict:
    # Synthetic example: support limits are stipulated as valid for this demo.
    strata = [
        Stratum(100, (0.0,) * 20 + (0.1,) * 20, 0.0, 0.2),
        Stratum(100, (0.4,) * 20 + (0.6,) * 20, 0.4, 1.0),
    ]
    strat = stratified_bounds(strata)
    global_ = global_support_bounds(strata, 0.0, 1.0)
    return {
        "population": sum(s.population for s in strata),
        "observed": sum(len(s.observed_values) for s in strata),
        "missing": sum(s.missing for s in strata),
        "stratified_bounds": [strat.lower, strat.upper],
        "stratified_width": strat.width,
        "global_bounds": [global_.lower, global_.upper],
        "global_width": global_.width,
        "width_reduction_fraction": 1.0 - strat.width / global_.width,
        "endpoint_attainability_checked": endpoints_are_attainable(strata),
        "status": "synthetic deterministic demonstration; support validity is an assumption",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
