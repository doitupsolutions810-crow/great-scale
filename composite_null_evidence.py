"""Fixed-sample robust evidence for a finite composite Bernoulli null.

This module intentionally does not claim sequential validity. The iid Bernoulli
assumption and fixed sample size must be justified outside this function.
"""
from __future__ import annotations
import math
from typing import Iterable, Sequence


def _probabilities(values: Sequence[float], name: str, *, allow_empty: bool = False) -> list[float]:
    result = [float(x) for x in values]
    if not result and not allow_empty:
        raise ValueError(f"{name} must not be empty")
    if any(not math.isfinite(x) or x < 0.0 or x > 1.0 for x in result):
        raise ValueError(f"{name} values must be finite probabilities in [0, 1]")
    return result


def _log_bernoulli_likelihood(successes: int, n: int, p: float) -> float:
    failures = n - successes
    if (p == 0.0 and successes > 0) or (p == 1.0 and failures > 0):
        return -math.inf
    value = 0.0
    if successes:
        value += successes * math.log(p)
    if failures:
        value += failures * math.log1p(-p)
    return value


def fixed_sample_robust_e_value(
    observations: Iterable[int],
    null_probabilities: Sequence[float],
    alternative_probabilities: Sequence[float],
    weights: Sequence[float],
) -> float:
    """Return mixture-alternative likelihood / worst-case finite-null likelihood.

    For each fixed sample size n and each q in null_probabilities, E_q[E] <= 1.
    This is a fixed-sample e-value, not an anytime-valid e-process.
    """
    xs = list(observations)
    if any(type(x) is not int or x not in (0, 1) for x in xs):
        raise ValueError("observations must contain only integer 0/1 values")
    nulls = _probabilities(null_probabilities, "null_probabilities")
    alts = _probabilities(alternative_probabilities, "alternative_probabilities")
    ws = [float(w) for w in weights]
    if len(alts) != len(ws):
        raise ValueError("weights length must match alternative_probabilities")
    if any(not math.isfinite(w) or w < 0.0 for w in ws):
        raise ValueError("weights must be finite and nonnegative")
    if not math.isclose(sum(ws), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("weights must sum to 1")
    if not xs:
        raise ValueError("observations must not be empty")

    s, n = sum(xs), len(xs)
    log_terms = []
    for p, w in zip(alts, ws):
        if w > 0.0:
            ll = _log_bernoulli_likelihood(s, n, p)
            log_terms.append(math.log(w) + ll)
    if not log_terms:
        raise ValueError("at least one alternative must have positive weight")
    max_log = max(log_terms)
    log_num = max_log + math.log(sum(math.exp(t - max_log) for t in log_terms))
    log_den = max(_log_bernoulli_likelihood(s, n, q) for q in nulls)
    if log_den == -math.inf:
        raise ValueError("observed sequence has zero probability under every null model")
    log_e = log_num - log_den
    if log_e > math.log(float.fromhex("0x1.fffffffffffffp+1023")):
        return math.inf
    return math.exp(log_e)


def fixed_sample_decision(e_value: float, alpha: float, *, assumptions_confirmed: bool = True) -> str:
    """Apply a predeclared fixed-sample threshold, with an assumptions gate."""
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be finite and in (0, 1)")
    if math.isnan(e_value) or e_value < 0.0:
        raise ValueError("e_value must be nonnegative and not NaN")
    if not assumptions_confirmed:
        return "ASSUMPTIONS_NOT_CONFIRMED"
    return "REJECT_NULL_AT_FIXED_SAMPLE" if e_value >= 1.0 / alpha else "INSUFFICIENT_EVIDENCE"
