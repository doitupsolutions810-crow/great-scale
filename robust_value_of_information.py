"""Robust value-of-information analysis across a finite set of plausible models."""
from __future__ import annotations
from typing import Mapping, Sequence
from active_measurement import expected_value_of_sample_information

def robust_measurement_value(models: Sequence[Mapping]) -> dict:
    """Each model supplies prior, likelihoods, utilities, and optional cost.

    Recommends MEASURE only when net value is positive in every supplied model.
    This is a finite-set robustness test, not proof the set is complete.
    """
    if not models:
        raise ValueError("models must contain at least one plausible model")
    results = []
    for index, model in enumerate(models):
        try:
            result = expected_value_of_sample_information(
                model["prior"], model["likelihoods"], model["utilities"], model.get("cost", 0.0))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid model at index {index}: {exc}") from exc
        results.append(result)
    nets = [float(item["net_value"]) for item in results]
    lower, upper = min(nets), max(nets)
    return {
        "model_count": len(results), "model_net_values": nets,
        "worst_case_net_value": lower, "best_case_net_value": upper,
        "net_value_range": [lower, upper],
        "recommendation": "MEASURE" if lower > 1e-12 else "NOT_ROBUSTLY_WORTH_MEASURING",
        "robustness_scope": "only the supplied finite model set",
    }
