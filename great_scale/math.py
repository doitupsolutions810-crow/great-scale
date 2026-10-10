"""Small, deterministic calculations used by Great Scale tests."""
from __future__ import annotations
import math
from collections.abc import Sequence


def weighted_time_variance(times: Sequence[float], weights: Sequence[float]) -> float:
    """Return sum_i w_i (t_i - weighted_mean)^2; weights must be positive."""
    if len(times) != len(weights) or not times:
        raise ValueError("times and weights must have the same non-zero length")
    if any(w <= 0 for w in weights):
        raise ValueError("weights must be positive")
    total = sum(weights)
    mean = sum(t * w for t, w in zip(times, weights)) / total
    return sum(w * (t - mean) ** 2 for t, w in zip(times, weights))


def pairwise_weighted_time_variance(times: Sequence[float], weights: Sequence[float]) -> float:
    """Equivalent pairwise identity: (1/W) sum_{i<j} w_i w_j (t_i-t_j)^2."""
    if len(times) != len(weights) or not times:
        raise ValueError("times and weights must have the same non-zero length")
    if any(w <= 0 for w in weights):
        raise ValueError("weights must be positive")
    total = sum(weights)
    return sum(weights[i] * weights[j] * (times[i] - times[j]) ** 2
               for i in range(len(times)) for j in range(i + 1, len(times))) / total


def relaxation_step(values: Sequence[float], rate: float) -> list[float]:
    """One exact discrete relaxation step toward the coordinate mean."""
    if not values:
        raise ValueError("values must not be empty")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    mean = sum(values) / len(values)
    return [mean + (x - mean) * (1 - rate) for x in values]


def close(a: float, b: float, tol: float = 1e-10) -> bool:
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)
