"""Great Scale CXXXIII: robust bounds when stratum support endpoints are uncertain."""
from dataclasses import dataclass
from math import isclose
from typing import Sequence


@dataclass(frozen=True)
class UncertainStratum:
    population: int
    observed_values: tuple[float, ...]
    lower_admissible: float
    lower_possible: float
    upper_possible: float
    upper_admissible: float

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


def _validate(strata: Sequence[UncertainStratum]) -> None:
    if not strata:
        raise ValueError("at least one stratum is required")
    for s in strata:
        if s.population < 1 or len(s.observed_values) > s.population:
            raise ValueError("invalid population or observed count")
        if not (s.lower_admissible <= s.lower_possible <= s.upper_possible <= s.upper_admissible):
            raise ValueError("support endpoint uncertainty ranges are inconsistent")
        if any(not (s.lower_admissible <= x <= s.upper_admissible) for x in s.observed_values):
            raise ValueError("observed value falls outside the outer admissible support")


def robust_bounds(strata: Sequence[UncertainStratum]) -> Bounds:
    """Uniformly valid bounds across all stated endpoint configurations."""
    _validate(strata)
    total = sum(s.population for s in strata)
    lo = sum(s.observed_sum + s.missing * s.lower_admissible for s in strata) / total
    hi = sum(s.observed_sum + s.missing * s.upper_admissible for s in strata) / total
    return Bounds(lo, hi)


def global_bounds(strata: Sequence[UncertainStratum], lower: float, upper: float) -> Bounds:
    _validate(strata)
    if lower > upper:
        raise ValueError("global lower support exceeds upper support")
    if any(not (lower <= x <= upper) for s in strata for x in s.observed_values):
        raise ValueError("observed value falls outside global support")
    total = sum(s.population for s in strata)
    observed = sum(s.observed_sum for s in strata)
    missing = sum(s.missing for s in strata)
    return Bounds((observed + missing * lower) / total,
                  (observed + missing * upper) / total)


def width_condition(strata: Sequence[UncertainStratum], global_lower: float,
                    global_upper: float) -> dict:
    """Compare missing-mass-weighted local span to the global support span."""
    _validate(strata)
    total = sum(s.population for s in strata)
    weighted_local_span = sum(s.missing * (s.upper_admissible - s.lower_admissible)
                              for s in strata) / total
    global_span_contribution = sum(s.missing for s in strata) * (global_upper-global_lower) / total
    return {
        "robust_width": weighted_local_span,
        "global_width": global_span_contribution,
        "strictly_tighter": weighted_local_span < global_span_contribution,
        "equal_width": isclose(weighted_local_span, global_span_contribution),
    }


def demo() -> dict:
    strata = [
        UncertainStratum(100, (0.0,) * 20 + (0.1,) * 20, 0.0, 0.05, 0.15, 0.2),
        UncertainStratum(100, (0.4,) * 20 + (0.6,) * 20, 0.35, 0.4, 0.9, 1.0),
    ]
    robust = robust_bounds(strata)
    global_ = global_bounds(strata, 0.0, 1.0)
    condition = width_condition(strata, 0.0, 1.0)
    return {
        "population": sum(s.population for s in strata),
        "observed": sum(len(s.observed_values) for s in strata),
        "missing": sum(s.missing for s in strata),
        "robust_bounds": [robust.lower, robust.upper],
        "robust_width": robust.width,
        "global_bounds": [global_.lower, global_.upper],
        "global_width": global_.width,
        "width_reduction_fraction": 1 - robust.width / global_.width,
        "width_condition": condition,
        "status": "deterministic synthetic example; support validity is assumed",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
