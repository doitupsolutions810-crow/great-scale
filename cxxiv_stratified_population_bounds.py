"""CXXIV: finite-population partial-identification bounds by known stratum.

Observed outcomes are treated as exact. Missing outcomes are bounded by valid
stratum-specific intervals. These are identification bounds, not confidence
intervals.
"""
from math import isfinite


def stratified_population_bounds(strata):
    """Return sharp lower/upper bounds for the overall finite-population mean.

    Input is a mapping: stratum -> {
      "total_count": known frame count,
      "observed_values": exact observed outcomes,
      "lower": valid lower outcome bound,
      "upper": valid upper outcome bound
    }.
    """
    if not strata:
        raise ValueError("at least one stratum is required")
    total_population = 0
    lower_sum = 0.0
    upper_sum = 0.0
    missing_total = 0
    details = {}
    for name, item in strata.items():
        total = item["total_count"]
        values = list(item["observed_values"])
        lower, upper = item["lower"], item["upper"]
        if not isinstance(total, int) or total < 0:
            raise ValueError(f"{name}: total_count must be a nonnegative integer")
        if not (isfinite(lower) and isfinite(upper) and lower <= upper):
            raise ValueError(f"{name}: invalid finite outcome bounds")
        if len(values) > total:
            raise ValueError(f"{name}: observed count exceeds total_count")
        if any(not isfinite(v) or v < lower or v > upper for v in values):
            raise ValueError(f"{name}: observed outcome outside valid bounds")
        missing = total - len(values)
        observed_sum = sum(values)
        lo = observed_sum + missing * lower
        hi = observed_sum + missing * upper
        total_population += total
        missing_total += missing
        lower_sum += lo
        upper_sum += hi
        details[name] = {
            "total_count": total, "observed_count": len(values),
            "missing_count": missing, "observed_sum": observed_sum,
            "lower_sum": lo, "upper_sum": hi,
            "lower_bound": lo / total if total else None,
            "upper_bound": hi / total if total else None,
        }
    if total_population == 0:
        raise ValueError("total population must be positive")
    return {
        "population_count": total_population,
        "missing_count": missing_total,
        "lower_bound": lower_sum / total_population,
        "upper_bound": upper_sum / total_population,
        "width": (upper_sum - lower_sum) / total_population,
        "strata": details,
    }


def unstratified_bounds(strata, lower, upper):
    """Comparator using one global interval for every missing outcome."""
    total = sum(item["total_count"] for item in strata.values())
    observed = [v for item in strata.values() for v in item["observed_values"]]
    if total <= 0 or len(observed) > total or not (isfinite(lower) and isfinite(upper) and lower <= upper):
        raise ValueError("invalid population size or global bounds")
    if any(not isfinite(v) or v < lower or v > upper for v in observed):
        raise ValueError("observed outcome outside global bounds")
    missing = total - len(observed)
    lo = sum(observed) + missing * lower
    hi = sum(observed) + missing * upper
    return {"population_count": total, "missing_count": missing,
            "lower_bound": lo / total, "upper_bound": hi / total,
            "width": (hi - lo) / total}
