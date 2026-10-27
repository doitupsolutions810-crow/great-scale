"""Anytime-valid evidence for Bernoulli data with conditional mean bounded.

Null assumption:
    E[X_t | F_{t-1}] <= q0 almost surely, with X_t in {0, 1}.

For a fixed predictable betting fraction lambda in [0, 1/q0], each factor
1 + lambda * (X_t - q0) is nonnegative and has conditional expectation <= 1.
Products are therefore nonnegative supermartingales under the null. A
predeclared convex mixture of these products is also an e-process.

This is a conditional-mean guarantee, not an iid likelihood-ratio model.
The bet fractions and mixture weights must be fixed before observing outcomes.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence


def conditional_mean_e_process(
    observations: Iterable[int],
    null_upper_bound: float,
    betting_fractions: Sequence[float],
    weights: Sequence[float],
) -> list[float]:
    """Return mixture e-values E_0,...,E_n for binary observations.

    Each betting fraction lambda must lie in [0, 1/q0]. The alternatives are
    betting strategies, not claimed data-generating distributions.
    """
    xs = list(observations)
    q0 = float(null_upper_bound)
    lambdas = [float(x) for x in betting_fractions]
    ws = [float(x) for x in weights]

    if not math.isfinite(q0) or not 0.0 < q0 < 1.0:
        raise ValueError("null_upper_bound must be finite and strictly between 0 and 1")
    if not lambdas or len(lambdas) != len(ws):
        raise ValueError("betting_fractions and weights must have equal nonzero length")
    if any(not math.isfinite(x) or x < 0.0 or x > 1.0 / q0 for x in lambdas):
        raise ValueError("each betting fraction must be finite and in [0, 1/q0]")
    if any(not math.isfinite(w) or w < 0.0 for w in ws):
        raise ValueError("weights must be finite and nonnegative")
    if not math.isclose(sum(ws), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("weights must sum to 1")
    if any(isinstance(x, bool) or x not in (0, 1) for x in xs):
        raise ValueError("observations must contain only integer 0 or 1 values")

    wealth = [1.0] * len(lambdas)
    result = [1.0]
    for x in xs:
        for i, lam in enumerate(lambdas):
            wealth[i] *= 1.0 + lam * (x - q0)
        result.append(sum(w * e for w, e in zip(ws, wealth)))
    return result


def sequential_decision(
    e_values: Sequence[float], alpha: float, assumptions_confirmed: bool = True
) -> dict[str, object]:
    """Apply Ville's 1/alpha threshold, gated on the stated assumptions."""
    a = float(alpha)
    if not math.isfinite(a) or not 0.0 < a < 1.0:
        raise ValueError("alpha must be finite and strictly between 0 and 1")
    if not e_values or any(not math.isfinite(float(e)) or float(e) < 0 for e in e_values):
        raise ValueError("e_values must be a nonempty sequence of finite nonnegative values")
    maximum = max(float(e) for e in e_values)
    crossed = maximum >= 1.0 / a
    if not assumptions_confirmed:
        status = "UNVERIFIED_ASSUMPTIONS"
    elif crossed:
        status = "EVIDENCE_THRESHOLD_CROSSED"
    else:
        status = "NO_THRESHOLD_CROSSING"
    return {
        "status": status,
        "threshold": 1.0 / a,
        "maximum_e_value": maximum,
        "threshold_crossed": crossed,
        "assumptions_confirmed": bool(assumptions_confirmed),
    }
