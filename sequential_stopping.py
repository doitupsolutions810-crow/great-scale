"""Sequential evidence utilities based on bounded likelihood ratios.

This module implements a narrow, auditable e-process for a simple-vs-simple
Bernoulli model. It is not a generic model-training monitor or a substitute
for validating the data-generating assumptions.
"""
from __future__ import annotations
import math
from typing import Iterable, Mapping, Any


def _probability(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1 inclusive")


def _positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 1:
        raise ValueError(f"{name} must be at least 1")


def independent_bernoulli_log_lr(observations: Iterable[int], p0: float, p1: float) -> float:
    """Log likelihood ratio log(P_p1(data)/P_p0(data)) for Bernoulli data."""
    _probability(p0, "p0")
    _probability(p1, "p1")
    if p0 == p1:
        raise ValueError("p0 and p1 must differ")
    xs = list(observations)
    if not xs:
        raise ValueError("observations must not be empty")
    if any(isinstance(x, bool) or not isinstance(x, int) or x not in (0, 1) for x in xs):
        raise ValueError("observations must contain only integer 0 or 1 values")
    successes = sum(xs)
    failures = len(xs) - successes
    def term(count: int, p_num: float, p_den: float) -> float:
        if count == 0:
            return 0.0
        if p_num == 0 or p_den == 0:
            return math.inf if p_num > 0 else -math.inf
        return count * math.log(p_num / p_den)
    return term(successes, p1, p0) + term(failures, 1-p1, 1-p0)


def bernoulli_e_process(observations: Iterable[int], p0: float, p1: float) -> float:
    """Likelihood-ratio e-value for a fixed alternative against Bernoulli p0.

    Under the null of independent Bernoulli(p0) observations, the likelihood
    ratio is a nonnegative martingale with expectation one, provided the
    sampling model and null are correct. At p0 boundary cases, an impossible
    null outcome yields +infinity; handle such degenerate models carefully.
    """
    log_lr = independent_bernoulli_log_lr(observations, p0, p1)
    if log_lr == math.inf:
        return math.inf
    if log_lr == -math.inf:
        return 0.0
    return math.exp(log_lr)


def evidence_threshold(alpha: float) -> float:
    """Ville threshold 1/alpha for a chosen type-I error budget alpha in (0,1)."""
    _probability(alpha, "alpha")
    if alpha == 0:
        raise ValueError("alpha must be greater than 0")
    if alpha == 1:
        return 1.0
    return 1.0 / alpha


def stopping_decision(e_value: float, alpha: float) -> str:
    """Reject the null only when e_value reaches the predeclared threshold."""
    if isinstance(e_value, bool) or not isinstance(e_value, (int, float)):
        raise TypeError("e_value must be numeric")
    if math.isnan(e_value) or e_value < 0:
        raise ValueError("e_value must be nonnegative and not NaN")
    return "EVIDENCE_THRESHOLD_REACHED" if e_value >= evidence_threshold(alpha) else "CONTINUE_OR_INCONCLUSIVE"


def audit_stopping_rule(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Audit a recorded sequence for valid increasing look indices and fixed alpha."""
    rows = list(events)
    issues: list[str] = []
    if not rows:
        raise ValueError("events must not be empty")
    previous_look = 0
    alpha_values: set[float] = set()
    stopped_at: int | None = None
    for i, event in enumerate(rows):
        look = event.get("look")
        alpha = event.get("alpha")
        stopped = event.get("stopped")
        if isinstance(look, bool) or not isinstance(look, int) or look <= previous_look:
            issues.append(f"event {i}: look indices must be strictly increasing positive integers")
        else:
            previous_look = look
        try:
            _probability(alpha, "alpha")
            if alpha == 0:
                raise ValueError("alpha must be greater than 0")
            alpha_values.add(float(alpha))
        except (TypeError, ValueError):
            issues.append(f"event {i}: invalid alpha")
        if not isinstance(stopped, bool):
            issues.append(f"event {i}: stopped must be bool")
        elif stopped:
            if stopped_at is not None:
                issues.append(f"event {i}: multiple stop events")
            stopped_at = look if isinstance(look, int) else None
    if len(alpha_values) > 1:
        issues.append("alpha changed across looks; predeclared error budget not preserved")
    if stopped_at is not None and any(
        isinstance(e.get("look"), int) and not isinstance(e.get("look"), bool) and e.get("look") > stopped_at
        for e in rows
    ):
        issues.append("events recorded after a stop")
    return {
        "valid_log": not issues,
        "look_count": len(rows),
        "stopped_at": stopped_at,
        "issues": issues,
    }
