"""CXXII: partial-identification bounds under unknown selection probabilities."""
from __future__ import annotations
import math
import random
from typing import Any
from statistics import mean
from cxx_selection_stress_tests import build_population

def selection_bounds(deltas: list[float], *, pi_min: float=0.2,
                     pi_max: float=0.8) -> dict[str, Any]:
    """Bound a weighted mean when each inclusion probability lies in [min,max].

    For nonnegative deltas, extrema occur by assigning the smallest weights to
    positive values for the lower bound and the largest weights to them for the
    upper bound, with opposite assignments to zero values. For general signed
    values this shortcut is not valid, so this function rejects negative values.
    """
    if not deltas:
        raise ValueError("deltas must not be empty")
    if any(not math.isfinite(x) or x < 0 for x in deltas):
        raise ValueError("deltas must be finite and nonnegative")
    if not (math.isfinite(pi_min) and math.isfinite(pi_max)
            and 0 < pi_min <= pi_max <= 1):
        raise ValueError("require 0 < pi_min <= pi_max <= 1")
    # Weight is 1/pi. For lower mean, give positive outcomes the smallest
    # weight and zero outcomes the largest; reverse for upper mean.
    w_low=1.0/pi_max
    w_high=1.0/pi_min
    low_num=sum(x*w_low for x in deltas if x > 0)
    high_num=sum(x*w_high for x in deltas if x > 0)
    zero_count=sum(x == 0 for x in deltas)
    lower=low_num/(sum(w_low for x in deltas if x > 0)+zero_count*w_high)
    upper=high_num/(sum(w_high for x in deltas if x > 0)+zero_count*w_low)
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
        # Actual selection process used only to create this synthetic sample.
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
                "The closed-form extrema here assume nonnegative contrasts; signed outcomes require a general optimization formulation.",
                "Synthetic data only; no causal claim."]}

if __name__ == "__main__":
    import json
    print(json.dumps(run_partial_identification_test(),indent=2,sort_keys=True))
