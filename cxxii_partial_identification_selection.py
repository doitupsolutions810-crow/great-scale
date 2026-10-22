"""CXXII: partial-identification bounds under unknown selection probabilities."""
from __future__ import annotations
import math
import random
from typing import Any
from statistics import mean
from cxx_selection_stress_tests import build_population

def selection_bounds(deltas: list[float], *, pi_min: float=0.2,
                     pi_max: float=0.8) -> dict[str, Any]:
    """Bound a weighted mean over independently bounded inclusion probabilities.

    Enumerates endpoint assignments after sorting nonnegative contrasts. The
    ratio's extrema occur at endpoint weights; for a lower bound, high weights
    are assigned to lower values and low weights to higher values, and vice
    versa for the upper bound. Signed contrasts are intentionally unsupported.
    """
    if not deltas:
        raise ValueError("deltas must not be empty")
    if any(not math.isfinite(x) or x < 0 for x in deltas):
        raise ValueError("deltas must be finite and nonnegative")
    if not (math.isfinite(pi_min) and math.isfinite(pi_max)
            and 0 < pi_min <= pi_max <= 1):
        raise ValueError("require 0 < pi_min <= pi_max <= 1")
    values=sorted(deltas)
    w_low=1.0/pi_max
    w_high=1.0/pi_min
    candidates_low=[]
    candidates_high=[]
    n=len(values)
    for k in range(n+1):
        # Lower: first k low values get high weights; rest get low weights.
        weights_low=[w_high]*k+[w_low]*(n-k)
        # Upper: first k low values get low weights; rest get high weights.
        weights_high=[w_low]*k+[w_high]*(n-k)
        candidates_low.append(sum(x*w for x,w in zip(values,weights_low))/sum(weights_low))
        candidates_high.append(sum(x*w for x,w in zip(values,weights_high))/sum(weights_high))
    lower=min(candidates_low)
    upper=max(candidates_high)
    return {"lower":lower,"upper":upper,"width":upper-lower,
            "n_observed":len(deltas),"pi_min":pi_min,"pi_max":pi_max}

def run_partial_identification_test(*, n_clusters: int=200, seed: int=20261010,
                                    pi_min: float=0.2, pi_max: float=0.8) -> dict[str, Any]:
    """Draw one selected sample and bound its weighted mean under probability ranges."""
    pop=build_population(n_clusters)
    truth=mean(c["delta"] for c in pop)
    rng=random.Random(seed)
    selected=[]
    for c in pop:
        pi=0.8 if c["delta"]>0 else 0.25
        if rng.random()<pi:
            selected.append(c["delta"])
    if not selected:
        raise RuntimeError("no clusters selected")
    bounds=selection_bounds(selected,pi_min=pi_min,pi_max=pi_max)
    return {"synthetic_only":True,"seed":seed,"n_clusters":n_clusters,
            "n_selected":len(selected),"known_finite_population_target":truth,
            "observed_equal_cluster_mean":mean(selected),"bounds":bounds,
            "target_inside_bounds":bounds["lower"] <= truth <= bounds["upper"],
            "limitations":[
                "Bounds apply to the selected sample's weighted mean under independent per-cluster probability ranges.",
                "They are not confidence intervals and do not automatically bound the full-population target under arbitrary selection.",
                "The probability interval must be justified externally; widening or narrowing it changes the result.",
                "Contrasts must be nonnegative; signed contrasts require a general optimization formulation.",
                "Synthetic data only; no causal claim."]}

if __name__ == "__main__":
    import json
    print(json.dumps(run_partial_identification_test(),indent=2,sort_keys=True))
