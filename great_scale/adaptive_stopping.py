"""Great Scale LXXXI: adaptive certification with a persistent bias floor.

All bounds are deterministic assumptions supplied by the caller:
|y_n - x| <= bias_bound + noise_bound(n).
A certificate is issued only if the full admissible interval lies on one side
of the reference. The 1/sqrt(n) helper is a planning model, not a universal
statistical guarantee.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import math
from typing import Iterable

@dataclass(frozen=True)
class StoppingResult:
    stopped: bool
    stop_index: int | None
    certified_side: int
    observed: float | None
    reference: float
    total_error_bound: float | None
    margin: float | None
    reason: str

def first_certified_observation(observations: Iterable[tuple[float, float]], reference: float) -> StoppingResult:
    """Return the first (observed_value, valid_error_bound) that certifies a side."""
    if not math.isfinite(reference):
        raise ValueError("reference must be finite")
    last = None
    for index, (observed, error_bound) in enumerate(observations):
        if not math.isfinite(observed) or not math.isfinite(error_bound):
            raise ValueError("observations and bounds must be finite")
        if error_bound < 0:
            raise ValueError("error bounds must be nonnegative")
        last = (observed, error_bound)
        gap = observed - reference
        margin = abs(gap) - error_bound
        if margin > 0:
            return StoppingResult(True, index, 1 if gap > 0 else -1, observed,
                                  reference, error_bound, margin,
                                  "first valid side certificate")
    if last is None:
        return StoppingResult(False, None, 0, None, reference, None, None,
                              "no observations supplied")
    observed, bound = last
    return StoppingResult(False, None, 0, observed, reference, bound,
                          max(0.0, abs(observed-reference)-bound),
                          "no observation certified a side")

def planned_minimum_n(gap: float, bias_floor: float, noise_scale: float) -> int | None:
    """Smallest n with gap > bias_floor + noise_scale/sqrt(n).

    Returns None when the asymptotic bias floor prevents certification.
    This is valid only when the caller can justify that error-bound model.
    """
    if not all(math.isfinite(v) for v in (gap, bias_floor, noise_scale)):
        raise ValueError("inputs must be finite")
    if gap < 0 or bias_floor < 0 or noise_scale < 0:
        raise ValueError("gap and bounds must be nonnegative")
    if gap <= bias_floor:
        return None
    if noise_scale == 0:
        return 1
    ratio_sq = (noise_scale / (gap - bias_floor)) ** 2
    return math.floor(ratio_sq) + 1

def as_record(result: StoppingResult) -> dict:
    return asdict(result)
