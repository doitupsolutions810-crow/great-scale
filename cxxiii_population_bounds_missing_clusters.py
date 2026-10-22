"""CXXIII: full-population bounds when some cluster outcomes are unobserved."""
from __future__ import annotations
import math
import random
from statistics import mean
from typing import Any
from cxx_selection_stress_tests import build_population

def population_mean_bounds(observed_values: list[float], *, population_size: int,
                           outcome_min: float, outcome_max: float) -> dict[str, Any]:
    """Bound a finite-population mean using a known frame and outcome limits.

    Each observed value is assumed measured without error and each missing
    cluster outcome is assumed to lie in [outcome_min, outcome_max].
    """
    if not isinstance(population_size,int) or population_size < 1:
        raise ValueError("population_size must be a positive integer")
    if len(observed_values) > population_size:
        raise ValueError("observed count cannot exceed population_size")
    if not (math.isfinite(outcome_min) and math.isfinite(outcome_max)
            and outcome_min <= outcome_max):
        raise ValueError("outcome limits must be finite and ordered")
    if any(not math.isfinite(x) or x < outcome_min or x > outcome_max
           for x in observed_values):
        raise ValueError("observed values must be finite and within outcome limits")
    missing=population_size-len(observed_values)
    observed_sum=sum(observed_values)
    lower=(observed_sum+missing*outcome_min)/population_size
    upper=(observed_sum+missing*outcome_max)/population_size
    return {"lower":lower,"upper":upper,"width":upper-lower,
            "population_size":population_size,"observed_count":len(observed_values),
            "missing_count":missing,"outcome_min":outcome_min,"outcome_max":outcome_max}

def run_population_bounds_test(*, n_clusters: int=200, seed: int=20261010,
                               outcome_min: float=0.0, outcome_max: float=0.25) -> dict[str, Any]:
    """Simulate selection, then bound the known finite-population mean."""
    pop=build_population(n_clusters)
    truth=mean(c["delta"] for c in pop)
    rng=random.Random(seed)
    observed=[]
    for c in pop:
        pi=0.8 if c["delta"]>0 else 0.25
        if rng.random() < pi:
            observed.append(c["delta"])
    if not observed:
        raise RuntimeError("no clusters selected")
    bounds=population_mean_bounds(observed,population_size=n_clusters,
                                 outcome_min=outcome_min,outcome_max=outcome_max)
    return {"synthetic_only":True,"seed":seed,"known_finite_population_target":truth,
            "observed_equal_cluster_mean":mean(observed),"bounds":bounds,
            "target_inside_bounds":bounds["lower"] <= truth <= bounds["upper"],
            "assumptions":[
                "Total population frame size is known.",
                "Observed cluster contrasts are measured without error.",
                "Every missing cluster contrast lies within the declared outcome limits."],
            "limitations":[
                "These are deterministic identification bounds, not confidence intervals.",
                "Bounds may be wide when many clusters are missing or outcome limits are broad.",
                "Validity depends on the population frame and outcome limits being defensible.",
                "Synthetic demonstration only; no causal claim."]}

if __name__ == "__main__":
    import json
    print(json.dumps(run_population_bounds_test(),indent=2,sort_keys=True))
