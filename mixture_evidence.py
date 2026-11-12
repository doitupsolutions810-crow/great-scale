"""Predeclared finite-mixture e-process for independent Bernoulli data.

The null is a fixed Bernoulli probability p0. Alternatives and nonnegative
weights summing to one must be fixed before observing the data. This does not
solve arbitrary composite-null or post-hoc adaptive-alternative problems.
"""
from __future__ import annotations
import math
from typing import Iterable, Sequence


def _probability(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1 inclusive")


def _observations(values: Iterable[int]) -> list[int]:
    xs = list(values)
    if not xs:
        raise ValueError("observations must not be empty")
    if any(isinstance(x, bool) or not isinstance(x, int) or x not in (0, 1) for x in xs):
        raise ValueError("observations must contain only integer 0 or 1 values")
    return xs


def _log_likelihood(xs: Sequence[int], p: float) -> float:
    successes = sum(xs)
    failures = len(xs) - successes
    if successes and p == 0:
        return -math.inf
    if failures and p == 1:
        return -math.inf
    result = 0.0
    if successes:
        result += successes * math.log(p)
    if failures:
        result += failures * math.log1p(-p)
    return result


def bernoulli_mixture_e_value(
    observations: Iterable[int], p0: float,
    alternatives: Sequence[float], weights: Sequence[float]
) -> float:
    """Compute sum_k w_k * P_pk(data)/P_p0(data) for a fixed mixture.

    For a nondegenerate fixed p0, each likelihood ratio is an e-process under
    the null. A fixed convex mixture remains an e-process. If the observed
    sequence has zero probability under p0, the ratio is undefined/infinite;
    this function raises rather than pretending that boundary case is routine.
    """
    _probability(p0, "p0")
    xs = _observations(observations)
    if p0 in (0, 1):
        raise ValueError("p0 must be strictly between 0 and 1")
    if not alternatives or len(alternatives) != len(weights):
        raise ValueError("alternatives and weights must have equal nonzero length")
    for p in alternatives:
        _probability(p, "alternative")
    for w in weights:
        _probability(w, "weight")
    if not math.isclose(sum(weights), 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError("weights must sum to 1")
    log_null = _log_likelihood(xs, p0)
    log_terms = []
    for p, w in zip(alternatives, weights):
        if w == 0:
            continue
        log_alt = _log_likelihood(xs, p)
        log_terms.append(math.log(w) + log_alt - log_null)
    if not log_terms:
        return 0.0
    maximum = max(log_terms)
    if maximum == math.inf:
        return math.inf
    if maximum == -math.inf:
        return 0.0
    log_sum = maximum + math.log(sum(math.exp(v - maximum) for v in log_terms))
    return math.exp(log_sum)


def threshold_reached(e_value: float, alpha: float) -> bool:
    _probability(alpha, "alpha")
    if alpha == 0:
        raise ValueError("alpha must be greater than 0")
    if isinstance(e_value, bool) or not isinstance(e_value, (int, float)):
        raise TypeError("e_value must be numeric")
    if math.isnan(e_value) or e_value < 0:
        raise ValueError("e_value must be nonnegative and not NaN")
    return e_value >= 1 / alpha
