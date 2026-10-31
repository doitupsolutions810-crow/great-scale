"""CXXV: robust population bounds when stratum limits are uncertain.

For each stratum, lower_range=[smallest defensible lower limit, largest
plausible lower limit] and upper_range=[smallest plausible upper limit,
largest defensible upper limit]. Robust bounds use the smallest lower limit
and largest upper limit. These remain identification bounds, not confidence
intervals.
"""
from math import isfinite


def robust_stratified_bounds(strata):
    if not strata:
        raise ValueError("at least one stratum is required")
    total_population = 0
    lower_sum = 0.0
    upper_sum = 0.0
    details = {}
    for name, item in strata.items():
        total = item["total_count"]
        values = list(item["observed_values"])
        lower_range = item["lower_range"]
        upper_range = item["upper_range"]
        if not isinstance(total, int) or total < 0 or len(values) > total:
            raise ValueError(f"{name}: invalid population or observed count")
        if len(lower_range) != 2 or len(upper_range) != 2:
            raise ValueError(f"{name}: limit ranges must each have two endpoints")
        ll, lu = lower_range
        ul, uu = upper_range
        if not all(isfinite(x) for x in (ll, lu, ul, uu)):
            raise ValueError(f"{name}: limits must be finite")
        if ll > lu or ul > uu or ll > ul:
            raise ValueError(f"{name}: inconsistent limit ranges")
        if any(not isfinite(v) or v < ll or v > uu for v in values):
            raise ValueError(f"{name}: observed value outside robust outer limits")
        missing = total - len(values)
        observed_sum = sum(values)
        lo_sum = observed_sum + missing * ll
        hi_sum = observed_sum + missing * uu
        total_population += total
        lower_sum += lo_sum
        upper_sum += hi_sum
        details[name] = {
            "total_count": total, "observed_count": len(values),
            "missing_count": missing, "observed_sum": observed_sum,
            "robust_lower_limit": ll, "robust_upper_limit": uu,
            "lower_sum": lo_sum, "upper_sum": hi_sum,
        }
    if total_population <= 0:
        raise ValueError("total population must be positive")
    return {
        "population_count": total_population,
        "missing_count": sum(v["missing_count"] for v in details.values()),
        "lower_bound": lower_sum / total_population,
        "upper_bound": upper_sum / total_population,
        "width": (upper_sum - lower_sum) / total_population,
        "strata": details,
    }


def nominal_stratified_bounds(strata):
    """Bounds using point-valued limits, for sensitivity comparison."""
    converted = {}
    for name, item in strata.items():
        lower, upper = item["lower"], item["upper"]
        converted[name] = {
            "total_count": item["total_count"],
            "observed_values": item["observed_values"],
            "lower_range": (lower, lower),
            "upper_range": (upper, upper),
        }
    return robust_stratified_bounds(converted)
