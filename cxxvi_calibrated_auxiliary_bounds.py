"""CXXVI: sensitivity bounds from auxiliary calibration samples.

The observed auxiliary minimum/maximum are not guaranteed population limits.
This module makes the expansion margin explicit and labels the result as
conditional on the outer limits being valid.
"""
from math import isfinite


def calibrate_outer_limits(auxiliary_values, margin=0.0):
    values = list(auxiliary_values)
    if not values:
        raise ValueError("auxiliary sample must be nonempty")
    if not isfinite(margin) or margin < 0:
        raise ValueError("margin must be finite and nonnegative")
    if any(not isfinite(v) for v in values):
        raise ValueError("auxiliary values must be finite")
    return max(0.0, min(values) - margin), max(values) + margin


def population_mean_bounds(strata):
    """strata: name -> total_count, observed_values, lower, upper."""
    if not strata:
        raise ValueError("at least one stratum is required")
    total = 0
    low_sum = high_sum = 0.0
    details = {}
    for name, s in strata.items():
        count, values = s["total_count"], list(s["observed_values"])
        lo, hi = s["lower"], s["upper"]
        if not isinstance(count, int) or count < 0 or len(values) > count:
            raise ValueError(f"{name}: invalid counts")
        if not (isfinite(lo) and isfinite(hi) and lo <= hi):
            raise ValueError(f"{name}: invalid limits")
        if any(not isfinite(v) or v < lo or v > hi for v in values):
            raise ValueError(f"{name}: observation outside limits")
        missing = count - len(values)
        observed_sum = sum(values)
        low_sum += observed_sum + missing * lo
        high_sum += observed_sum + missing * hi
        total += count
        details[name] = {"total_count": count, "observed_count": len(values),
                         "missing_count": missing, "lower": lo, "upper": hi}
    if total <= 0:
        raise ValueError("total population must be positive")
    return {"population_count": total, "lower_bound": low_sum / total,
            "upper_bound": high_sum / total, "width": (high_sum-low_sum)/total,
            "strata": details}


def build_bounds_from_auxiliary(auxiliary_by_stratum, observed_by_stratum,
                                total_counts, margin=0.0):
    if set(auxiliary_by_stratum) != set(total_counts) or set(observed_by_stratum) != set(total_counts):
        raise ValueError("stratum keys must match across inputs")
    strata = {}
    for name in total_counts:
        lo, hi = calibrate_outer_limits(auxiliary_by_stratum[name], margin)
        strata[name] = {"total_count": total_counts[name],
                        "observed_values": observed_by_stratum[name],
                        "lower": lo, "upper": hi}
    return population_mean_bounds(strata)
