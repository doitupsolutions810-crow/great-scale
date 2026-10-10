"""Observability limits for Great Scale XC.

These functions calculate theoretical limits from a supplied total-variation
bound. They do not estimate the true distance or validate a detector.
"""
from __future__ import annotations

import math


def _unit_interval(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and in [0, 1]")
    return value


def detection_power_upper_bound(false_positive_rate: float, tv_distance_upper: float) -> float:
    """Bound detector power by min(1, alpha + TV(P0, P1)).

    For any fixed event/test, the difference between its probabilities under
    P0 and P1 is at most their total variation distance.
    """
    alpha = _unit_interval(false_positive_rate, "false_positive_rate")
    tv = _unit_interval(tv_distance_upper, "tv_distance_upper")
    return min(1.0, alpha + tv)


def distinguishability_gap(tv_distance_upper: float) -> float:
    """Return upper bound on the absolute probability gap for any event/test."""
    return _unit_interval(tv_distance_upper, "tv_distance_upper")


def detector_disposition(
    false_positive_rate: float,
    tv_distance_upper: float,
    required_power: float,
) -> str:
    """Assess whether the supplied TV bound can certify the requested power."""
    required_power = _unit_interval(required_power, "required_power")
    upper = detection_power_upper_bound(false_positive_rate, tv_distance_upper)
    return "POWER_POSSIBLE_NOT_GUARANTEED" if upper >= required_power else "POWER_REQUIREMENT_IMPOSSIBLE_UNDER_BOUND"


def minimum_tv_needed(false_positive_rate: float, required_power: float) -> float:
    """Necessary TV separation for power >= target at the supplied false-positive rate."""
    alpha = _unit_interval(false_positive_rate, "false_positive_rate")
    power = _unit_interval(required_power, "required_power")
    return max(0.0, power - alpha)
