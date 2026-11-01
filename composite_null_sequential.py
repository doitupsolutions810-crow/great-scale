"""Anytime-valid upper-tail e-process for a Bernoulli composite null.

Null: iid Bernoulli(q) with q <= q0. Alternatives are fixed probabilities p > q0.
The q0 boundary likelihood ratio is a supermartingale under every null q <= q0.
This module does not handle two-sided, arbitrary finite, or dependent nulls.
"""
import math
from typing import Iterable, Sequence


def _validate_prob(x, name):
    x = float(x)
    if not math.isfinite(x) or not 0.0 < x < 1.0:
        raise ValueError(f"{name} must be finite and strictly between 0 and 1")
    return x


def bernoulli_upper_null_e_process(
    observations: Iterable[int],
    null_upper_bound: float,
    alternative_probabilities: Sequence[float],
    weights: Sequence[float],
) -> list[float]:
    """Return E_0,...,E_n for a predeclared mixture of alternatives > null bound.

    Under iid Bernoulli(q) for any q <= null_upper_bound, this is a
    nonnegative supermartingale starting at 1. Its threshold crossing obeys
    Ville's inequality. Alternatives and weights must be fixed in advance.
    """
    q0 = _validate_prob(null_upper_bound, "null_upper_bound")
    xs = list(observations)
    if any(type(x) is not int or x not in (0, 1) for x in xs):
        raise ValueError("observations must contain only integer 0/1 values")
    ps = [float(p) for p in alternative_probabilities]
    ws = [float(w) for w in weights]
    if not ps or len(ps) != len(ws):
        raise ValueError("nonempty alternatives and matching weights are required")
    if any(not math.isfinite(p) or p <= q0 or p > 1.0 for p in ps):
        raise ValueError("each alternative probability must be in (null_upper_bound, 1]")
    if any(not math.isfinite(w) or w < 0.0 for w in ws):
        raise ValueError("weights must be finite and nonnegative")
    if not math.isclose(sum(ws), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("weights must sum to 1")
    if not any(w > 0 for w in ws):
        raise ValueError("at least one alternative must have positive weight")

    logs = [math.log(w) if w > 0 else -math.inf for w in ws]
    values = [1.0]
    for x in xs:
        for i, p in enumerate(ps):
            if ws[i] == 0:
                continue
            if x == 1:
                logs[i] += math.log(p / q0)
            elif p == 1.0:
                logs[i] = -math.inf
            else:
                logs[i] += math.log((1.0 - p) / (1.0 - q0))
        finite = [v for v in logs if v != -math.inf]
        if not finite:
            values.append(0.0)
            continue
        m = max(finite)
        log_e = m + math.log(sum(math.exp(v - m) for v in logs if v != -math.inf))
        values.append(math.exp(log_e) if log_e < 709 else math.inf)
    return values


def sequential_decision(e_values: Sequence[float], alpha: float, *, assumptions_confirmed: bool = True) -> str:
    """Classify threshold crossing only if the model assumptions are confirmed."""
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be finite and in (0, 1)")
    if not e_values or any(math.isnan(float(v)) or float(v) < 0 for v in e_values):
        raise ValueError("e_values must be a nonempty sequence of nonnegative non-NaN values")
    if not assumptions_confirmed:
        return "ASSUMPTIONS_NOT_CONFIRMED"
    return "REJECT_NULL_SEQUENTIALLY" if max(e_values) >= 1.0 / alpha else "NO_THRESHOLD_CROSSING"
