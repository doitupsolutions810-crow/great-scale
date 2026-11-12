"""Great Scale CXXXIV: robust bounds with uncertain missing-unit stratum counts."""
from dataclasses import dataclass
from itertools import product
from typing import Sequence


@dataclass(frozen=True)
class StratumCountRange:
    observed_sum: float
    observed_count: int
    missing_min: int
    missing_max: int
    lower: float
    upper: float

@dataclass(frozen=True)
class Bounds:
    lower: float
    upper: float
    lower_allocation: tuple[int, ...]
    upper_allocation: tuple[int, ...]
    @property
    def width(self) -> float:
        return self.upper - self.lower


def robust_count_bounds(strata: Sequence[StratumCountRange], total_missing: int) -> Bounds:
    """Exact finite enumeration over admissible integer missing-count allocations.

    Assumes observed membership/sums are known; only missing-unit allocation
    counts are uncertain. Each stratum support must cover all assigned missing
    outcomes. Raises if no count allocation satisfies all ranges.
    """
    if not strata:
        raise ValueError("at least one stratum is required")
    for s in strata:
        if s.observed_count < 0 or s.missing_min < 0 or s.missing_max < s.missing_min:
            raise ValueError("invalid observed count or missing-count range")
        if s.lower > s.upper:
            raise ValueError("lower support exceeds upper support")
    total_population = sum(s.observed_count for s in strata) + total_missing
    if total_missing < 0 or total_population <= 0:
        raise ValueError("invalid total missing count")
    candidates = []
    for allocation in product(*(range(s.missing_min, s.missing_max + 1) for s in strata)):
        if sum(allocation) != total_missing:
            continue
        lo = sum(s.observed_sum + m * s.lower for s, m in zip(strata, allocation)) / total_population
        hi = sum(s.observed_sum + m * s.upper for s, m in zip(strata, allocation)) / total_population
        candidates.append((lo, hi, tuple(allocation)))
    if not candidates:
        raise ValueError("no admissible missing-count allocation matches total_missing")
    lower_candidate = min(candidates, key=lambda x: x[0])
    upper_candidate = max(candidates, key=lambda x: x[1])
    return Bounds(lower_candidate[0], upper_candidate[1],
                  lower_candidate[2], upper_candidate[2])


def fixed_count_bounds(strata: Sequence[StratumCountRange], allocation: Sequence[int]) -> Bounds:
    if len(strata) != len(allocation) or any(m < 0 for m in allocation):
        raise ValueError("allocation must match strata and be nonnegative")
    total_missing = sum(allocation)
    total_population = sum(s.observed_count for s in strata) + total_missing
    if total_population <= 0:
        raise ValueError("population must be positive")
    return Bounds(
        sum(s.observed_sum + m*s.lower for s, m in zip(strata, allocation))/total_population,
        sum(s.observed_sum + m*s.upper for s, m in zip(strata, allocation))/total_population,
        tuple(allocation), tuple(allocation))


def demo() -> dict:
    strata = [
        StratumCountRange(observed_sum=2.0, observed_count=40, missing_min=40, missing_max=80, lower=0.0, upper=0.2),
        StratumCountRange(observed_sum=20.0, observed_count=40, missing_min=40, missing_max=80, lower=0.4, upper=1.0),
    ]
    b = robust_count_bounds(strata, total_missing=120)
    return {
        "total_population": 200, "observed_count": 80, "missing_count": 120,
        "bounds": [b.lower, b.upper], "width": b.width,
        "lower_worst_case_allocation": list(b.lower_allocation),
        "upper_worst_case_allocation": list(b.upper_allocation),
        "status": "exact finite enumeration for a synthetic example; membership ranges and supports are assumptions"
    }

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
