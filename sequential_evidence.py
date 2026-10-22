"""Sequential evidence and multiplicity controls for Great Scale LXXXVIII.

These helpers implement thresholds only. They cannot certify that a supplied
e-process is statistically valid or that a detected association is causal.
"""
from __future__ import annotations

import math


def _probability_open_unit(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 < value < 1.0:
        raise ValueError(f"{name} must be finite and strictly between 0 and 1")
    return value


def bonferroni_alpha(alpha: float, candidate_count: int) -> float:
    """Return per-candidate family-wise error allocation alpha / m."""
    alpha = _probability_open_unit(alpha, "alpha")
    if isinstance(candidate_count, bool) or not isinstance(candidate_count, int) or candidate_count < 1:
        raise ValueError("candidate_count must be a positive integer")
    return alpha / candidate_count


def ville_threshold(alpha: float) -> float:
    """Threshold 1/alpha for a valid nonnegative e-process under its null."""
    alpha = _probability_open_unit(alpha, "alpha")
    return 1.0 / alpha


def sequential_disposition(e_value: float, alpha: float) -> str:
    """Return a threshold disposition; not crossing is not acceptance of the null."""
    e_value = float(e_value)
    if math.isnan(e_value) or e_value < 0.0:
        raise ValueError("e_value must be nonnegative and not NaN")
    return (
        "CROSSING_THRESHOLD_ELIGIBLE_FOR_REVIEW"
        if e_value >= ville_threshold(alpha)
        else "CONTINUE_OR_INCONCLUSIVE"
    )


def sprt_wald_boundaries(alpha: float, beta: float) -> tuple[float, float]:
    """Return classical Wald approximate LR boundaries (A, B).

    For simple hypotheses and suitable sequential likelihood ratios:
    LR >= A favors H1; LR <= B favors H0. These are approximations, not
    guaranteed exact finite-sample error rates.
    """
    alpha = _probability_open_unit(alpha, "alpha")
    beta = _probability_open_unit(beta, "beta")
    return (1.0 - beta) / alpha, beta / (1.0 - alpha)
