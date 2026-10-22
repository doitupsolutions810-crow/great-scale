"""Distribution-shift transfer bounds for Great Scale LXXXIX.

These functions evaluate a supplied bound. They do not estimate the true
distance between distributions or certify that deployment assumptions hold.
"""
from __future__ import annotations

import math


def _finite_nonnegative(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def bounded_risk_transfer_bound(
    historical_risk_upper: float,
    loss_bound: float,
    total_variation_upper: float,
) -> float:
    """Upper-bound current risk by historical risk + M * TV(P, Q).

    Preconditions: loss lies in [0, loss_bound], historical_risk_upper is a
    valid upper bound on risk under P, and total_variation_upper is a valid
    upper bound on TV(P, Q). The result is clipped to loss_bound.
    """
    historical_risk_upper = _finite_nonnegative(historical_risk_upper, "historical_risk_upper")
    loss_bound = _finite_nonnegative(loss_bound, "loss_bound")
    total_variation_upper = _finite_nonnegative(total_variation_upper, "total_variation_upper")
    if historical_risk_upper > loss_bound:
        raise ValueError("historical_risk_upper cannot exceed loss_bound")
    if total_variation_upper > 1:
        raise ValueError("total_variation_upper must be in [0, 1]")
    return min(loss_bound, historical_risk_upper + loss_bound * total_variation_upper)


def transfer_status(
    historical_risk_upper: float,
    loss_bound: float,
    total_variation_upper: float,
    maximum_acceptable_risk: float,
) -> str:
    """Classify a supplied bound; does not infer distribution distance."""
    maximum_acceptable_risk = _finite_nonnegative(maximum_acceptable_risk, "maximum_acceptable_risk")
    bound = bounded_risk_transfer_bound(
        historical_risk_upper, loss_bound, total_variation_upper
    )
    return "BOUND_WITHIN_LIMIT" if bound <= maximum_acceptable_risk else "TRANSFER_NOT_CERTIFIED"


def risk_shift_budget(
    historical_risk_upper: float,
    loss_bound: float,
    maximum_acceptable_risk: float,
) -> float:
    """Largest TV upper bound permitted by the risk budget, in [0, 1].

    Returns zero when no positive shift is affordable. If loss_bound is zero,
    any TV distance has zero bounded loss impact and the returned budget is 1.
    """
    historical_risk_upper = _finite_nonnegative(historical_risk_upper, "historical_risk_upper")
    loss_bound = _finite_nonnegative(loss_bound, "loss_bound")
    maximum_acceptable_risk = _finite_nonnegative(maximum_acceptable_risk, "maximum_acceptable_risk")
    if historical_risk_upper > loss_bound:
        raise ValueError("historical_risk_upper cannot exceed loss_bound")
    if historical_risk_upper > maximum_acceptable_risk:
        return 0.0
    if loss_bound == 0:
        return 1.0
    return min(1.0, (maximum_acceptable_risk - historical_risk_upper) / loss_bound)
