"""Certified fixed-moment risk envelopes for two convex barrier-loss families.

This module separates a sharp fixed-moment envelope from a conservative
uncertain-moment chord bound. It does not claim a globally sharp robust
maximizer over an interval of means/variances.
"""
from __future__ import annotations

from math import isfinite, log1p, sqrt
from typing import Any, Dict

SCHEMA = "great-scale.loss-envelope/v1"
NEGATIVE_LOG = "negative_log"
POWER_BARRIER = "power_barrier"
SUPPORTED_LOSSES = (NEGATIVE_LOG, POWER_BARRIER)


def _validate_loss(loss: str, scale: float, power: float) -> tuple[float, float]:
    if loss not in SUPPORTED_LOSSES:
        raise ValueError(f"unsupported loss family: {loss!r}")
    scale = float(scale)
    power = float(power)
    if not isfinite(scale) or scale <= 0.0:
        raise ValueError("loss scale must be finite and positive")
    if loss == POWER_BARRIER and (not isfinite(power) or power <= 0.0):
        raise ValueError("power-barrier exponent must be finite and positive")
    return scale, power


def _support_from_margin(epsilon_lower: float) -> tuple[float, float]:
    epsilon = float(epsilon_lower)
    if not isfinite(epsilon) or not 0.0 < epsilon <= 1.0:
        raise ValueError("epsilon_lower must lie in (0, 1]")
    b = 1.0 - epsilon
    # Reject a margin too small to be represented distinctly from one.
    if not 0.0 <= b < 1.0:
        raise ValueError("support cap must be representable and strictly below 1")
    return epsilon, b


def loss_value(
    loss: str,
    x: float,
    *,
    scale: float = 1.0,
    power: float = 1.0,
) -> float:
    """Evaluate f(x) on 0 <= x < 1; scale is positive and power applies to barriers."""
    scale, power = _validate_loss(loss, scale, power)
    x = float(x)
    if not isfinite(x) or not 0.0 <= x < 1.0:
        raise ValueError("loss input x must be finite and in [0, 1)")
    if loss == NEGATIVE_LOG:
        return -scale * log1p(-x)
    try:
        value = scale * ((1.0 - x) ** (-power) - 1.0)
    except OverflowError as exc:
        raise ValueError("power-barrier loss exceeds floating-point range") from exc
    if not isfinite(value):
        raise ValueError("power-barrier loss exceeds floating-point range")
    return value


def loss_derivative(
    loss: str,
    x: float,
    *,
    scale: float = 1.0,
    power: float = 1.0,
) -> float:
    """Analytic first derivative for the supported loss families."""
    scale, power = _validate_loss(loss, scale, power)
    x = float(x)
    if not isfinite(x) or not 0.0 <= x < 1.0:
        raise ValueError("loss input x must be finite and in [0, 1)")
    if loss == NEGATIVE_LOG:
        return scale / (1.0 - x)
    try:
        value = scale * power * ((1.0 - x) ** (-power - 1.0))
    except OverflowError as exc:
        raise ValueError("power-barrier derivative exceeds floating-point range") from exc
    if not isfinite(value):
        raise ValueError("power-barrier derivative exceeds floating-point range")
    return value


def loss_third_derivative(
    loss: str,
    x: float,
    *,
    scale: float = 1.0,
    power: float = 1.0,
) -> float:
    """Analytic f'''(x), strictly positive on [0, b] for both supported families."""
    scale, power = _validate_loss(loss, scale, power)
    x = float(x)
    if not isfinite(x) or not 0.0 <= x < 1.0:
        raise ValueError("loss input x must be finite and in [0, 1)")
    if loss == NEGATIVE_LOG:
        return 2.0 * scale / ((1.0 - x) ** 3)
    try:
        value = (
            scale * power * (power + 1.0) * (power + 2.0)
            * ((1.0 - x) ** (-power - 3.0))
        )
    except OverflowError as exc:
        raise ValueError("power-barrier third derivative exceeds floating-point range") from exc
    if not isfinite(value):
        raise ValueError("power-barrier third derivative exceeds floating-point range")
    return value


def fixed_moment_envelope(
    mean: float,
    variance: float,
    epsilon_lower: float,
    *,
    loss: str = NEGATIVE_LOG,
    scale: float = 1.0,
    power: float = 1.0,
) -> Dict[str, Any]:
    """Return the sharp fixed-mean/variance upper envelope.

    Support is P in [0, b], b = 1 - epsilon_lower < 1.
    For f''' >= 0, the quadratic Hermite interpolant at c (double node) and b
    is a pointwise majorant. The equality witness puts mass alpha at b and
    1-alpha at c = mean - variance / (b - mean).
    """
    scale, power = _validate_loss(loss, scale, power)
    epsilon, b = _support_from_margin(epsilon_lower)
    mean, variance = float(mean), float(variance)
    if not isfinite(mean) or not isfinite(variance):
        raise ValueError("mean and variance must be finite")
    if not 0.0 <= mean <= b:
        raise ValueError("mean must lie within the support [0, b]")
    if variance < 0.0:
        raise ValueError("variance must be nonnegative")
    max_variance = mean * (b - mean)
    if variance > max_variance:
        raise ValueError("moments infeasible: variance exceeds mean*(b-mean)")

    if variance == 0.0:
        c = mean
        alpha = 0.0
    elif mean < b:
        c = mean - variance / (b - mean)
        alpha = variance / (((b - mean) ** 2) + variance)
        if not 0.0 <= c <= mean or not 0.0 <= alpha <= 1.0:
            raise ArithmeticError("computed extremal witness fell outside the feasible domain")
    else:
        # At mean=b the support constraint forces variance=0, handled above.
        raise ValueError("moments infeasible at mean=b")

    loss_c = loss_value(loss, c, scale=scale, power=power)
    loss_b = loss_value(loss, b, scale=scale, power=power)
    expected_loss = (1.0 - alpha) * loss_c + alpha * loss_b
    reconstructed_mean = (1.0 - alpha) * c + alpha * b
    reconstructed_variance = (
        (1.0 - alpha) * (c - mean) ** 2 + alpha * (b - mean) ** 2
    )
    if not isfinite(expected_loss):
        raise ValueError("fixed-moment envelope exceeds floating-point range")

    return {
        "schema": SCHEMA,
        "method": "SHARP_FIXED_MOMENT",
        "status": "PROVED_FIXED_MOMENT",
        "loss_family": loss,
        "scale": scale,
        "power": power if loss == POWER_BARRIER else None,
        "epsilon_lower": epsilon,
        "support": [0.0, b],
        "mean": mean,
        "variance": variance,
        "max_feasible_variance": max_variance,
        "bound": expected_loss,
        "witness": [
            {"point": c, "probability": 1.0 - alpha},
            {"point": b, "probability": alpha},
        ],
        "witness_moments": {
            "mean": reconstructed_mean,
            "variance": reconstructed_variance,
            "mean_abs_error": abs(reconstructed_mean - mean),
            "variance_abs_error": abs(reconstructed_variance - variance),
        },
        "third_derivative_lower_bound": loss_third_derivative(
            loss, 0.0, scale=scale, power=power
        ),
        "robust_global_maximum": None,
        "robust_global_status": "NOT_COMPUTED",
    }


def _feasible_moment_box(
    p_low: float,
    p_high: float,
    v_low: float,
    v_high: float,
    b: float,
) -> Dict[str, Any]:
    """Intersect input intervals with 0<=p<=b and 0<=v<=p(b-p)."""
    values = [float(p_low), float(p_high), float(v_low), float(v_high)]
    if not all(isfinite(x) for x in values):
        raise ValueError("moment interval endpoints must be finite")
    p_low, p_high, v_low, v_high = values
    if p_low > p_high:
        raise ValueError("mean interval is reversed")
    if v_low < 0.0 or v_high < v_low:
        raise ValueError("variance interval must satisfy 0 <= v_low <= v_high")

    # p(b-p)>=v_low is equivalent to the interval bounded by these roots.
    if b == 0.0:
        root_low = root_high = 0.0
    else:
        discriminant = (b * b / 4.0) - v_low
        if discriminant < 0.0:
            raise ValueError("empty feasible moment set: minimum variance exceeds b^2/4")
        radius = sqrt(discriminant)
        root_low = b / 2.0 - radius
        root_high = b / 2.0 + radius

    feasible_p_low = max(0.0, p_low, root_low)
    feasible_p_high = min(b, p_high, root_high)
    if feasible_p_low > feasible_p_high:
        raise ValueError("empty feasible moment set after support/variance intersection")

    p_star = min(max(b / 2.0, feasible_p_low), feasible_p_high)
    max_feasible_variance = p_star * (b - p_star)
    feasible_v_high = min(v_high, max_feasible_variance)
    if feasible_v_high < v_low:
        raise ValueError("empty feasible moment set: variance interval is infeasible")

    return {
        "input_mean_interval": [p_low, p_high],
        "input_variance_interval": [v_low, v_high],
        "feasible_mean_interval": [feasible_p_low, feasible_p_high],
        "feasible_variance_interval": [v_low, feasible_v_high],
        "max_feasible_variance": max_feasible_variance,
    }


def robust_chord_bound(
    p_low: float,
    p_high: float,
    v_low: float,
    v_high: float,
    epsilon_lower: float,
    *,
    loss: str = NEGATIVE_LOG,
    scale: float = 1.0,
    power: float = 1.0,
) -> Dict[str, Any]:
    """Certified conservative bound over interval-valued moments.

    This routine intentionally does not label max U_*(p,v) as sharp. It uses
    f(x) <= (x/b)f(b) on [0,b], so E[f(P)] <= p_upper*f(b)/b. The feasible
    p_upper is derived after intersecting the supplied moment box with the
    support and minimum-variance constraints.
    """
    scale, power = _validate_loss(loss, scale, power)
    epsilon, b = _support_from_margin(epsilon_lower)
    feasible = _feasible_moment_box(p_low, p_high, v_low, v_high, b)
    if b == 0.0:
        bound = 0.0
    else:
        p_upper = feasible["feasible_mean_interval"][1]
        bound = (p_upper / b) * loss_value(loss, b, scale=scale, power=power)
    if not isfinite(bound):
        raise ValueError("chord bound exceeds floating-point range")
    return {
        "schema": SCHEMA,
        "method": "CHORD_FALLBACK",
        "status": "CERTIFIED_ANALYTIC_BOUND",
        "loss_family": loss,
        "scale": scale,
        "power": power if loss == POWER_BARRIER else None,
        "epsilon_lower": epsilon,
        "support": [0.0, b],
        **feasible,
        "bound": bound,
        "robust_global_maximum": None,
        "robust_global_status": "NOT_CERTIFIED",
    }
