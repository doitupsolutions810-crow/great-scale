"""Active measurement utilities for Great Scale rung XCI."""
from __future__ import annotations
import math
from typing import Sequence

def _probability_vector(values: Sequence[float], name: str) -> list[float]:
    if not values:
        raise ValueError(f"{name} must not be empty")
    result = [float(v) for v in values]
    if any(not math.isfinite(v) or v < 0 for v in result):
        raise ValueError(f"{name} must contain finite non-negative values")
    if not math.isclose(sum(result), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"{name} must sum to 1")
    return result

def _validated_model(prior, likelihoods):
    p = _probability_vector(prior, "prior")
    if len(likelihoods) != len(p):
        raise ValueError("likelihoods must have one row per hypothesis")
    rows = [_probability_vector(row, f"likelihoods[{i}]") for i, row in enumerate(likelihoods)]
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("likelihood rows must have the same nonzero length")
    return p, rows

def entropy(probabilities: Sequence[float]) -> float:
    """Shannon entropy in nats for a normalized probability vector."""
    p = _probability_vector(probabilities, "probabilities")
    return -sum(v * math.log(v) for v in p if v > 0)

def information_gain(prior: Sequence[float], likelihoods: Sequence[Sequence[float]]) -> float:
    """Mutual information I(H;Y), in nats; likelihoods[h][y]=P(Y=y|H=h)."""
    p, rows = _validated_model(prior, likelihoods)
    py = [sum(p[h] * rows[h][y] for h in range(len(p))) for y in range(len(rows[0]))]
    prior_entropy = entropy(p)
    expected_posterior_entropy = 0.0
    for y, probability_y in enumerate(py):
        if probability_y == 0:
            continue
        posterior = [p[h] * rows[h][y] / probability_y for h in range(len(p))]
        expected_posterior_entropy += probability_y * entropy(posterior)
    return max(0.0, prior_entropy - expected_posterior_entropy)

def expected_value_of_sample_information(prior: Sequence[float],
        likelihoods: Sequence[Sequence[float]], utilities: Sequence[Sequence[float]],
        cost: float = 0.0) -> dict[str, float | str]:
    """Compute EVSI; utilities[d][h] is utility of decision d in state h."""
    p, rows = _validated_model(prior, likelihoods)
    if not math.isfinite(float(cost)) or cost < 0:
        raise ValueError("cost must be finite and non-negative")
    if not utilities:
        raise ValueError("utilities must contain at least one decision")
    u = [[float(v) for v in row] for row in utilities]
    if any(len(row) != len(p) for row in u):
        raise ValueError("each utility row must have one value per hypothesis")
    if any(not math.isfinite(v) for row in u for v in row):
        raise ValueError("utilities must be finite")
    py = [sum(p[h] * rows[h][y] for h in range(len(p))) for y in range(len(rows[0]))]
    prior_best = max(sum(p[h] * u[d][h] for h in range(len(p))) for d in range(len(u)))
    after_best = 0.0
    for y, probability_y in enumerate(py):
        if probability_y == 0:
            continue
        posterior = [p[h] * rows[h][y] / probability_y for h in range(len(p))]
        after_best += probability_y * max(
            sum(posterior[h] * u[d][h] for h in range(len(p))) for d in range(len(u)))
    evsi = max(0.0, after_best - prior_best)
    net = evsi - float(cost)
    return {"information_gain_nats": information_gain(p, rows), "evsi": evsi,
            "cost": float(cost), "net_value": net,
            "recommendation": "MEASURE" if net > 1e-12 else "DO_NOT_MEASURE"}
