"""CXXI: sensitivity of inverse-probability weighting to misspecified inclusion.

Uses the CXX finite synthetic population. All conclusions are simulation-only.
"""
from __future__ import annotations
import math
import random
from statistics import mean, pstdev
from typing import Any
from cxx_selection_stress_tests import build_population

def _logit(p: float) -> float:
    return math.log(p / (1.0-p))

def _expit(x: float) -> float:
    if x >= 0:
        z=math.exp(-x); return 1.0/(1.0+z)
    z=math.exp(x); return z/(1.0+z)

def run_misspecification_test(*, n_clusters: int=200, simulations: int=2000,
                              seed: int=20261010, logit_shift: float=1.0,
                              min_probability: float=0.02) -> dict[str, Any]:
    """Compare unweighted, true-probability IPW, and shifted-logit IPW.

    Selection follows CXX's effect-correlated design: pi=.8 when delta>0,
    otherwise pi=.25. Estimated inclusion probabilities are expit(logit(pi)+
    logit_shift), intentionally misspecified unless shift is zero.
    """
    if not isinstance(simulations,int) or simulations < 100:
        raise ValueError("simulations must be an integer >= 100")
    if not math.isfinite(logit_shift):
        raise ValueError("logit_shift must be finite")
    if not 0 < min_probability < 0.5:
        raise ValueError("min_probability must be between 0 and 0.5")
    pop=build_population(n_clusters)
    truth=mean(c["delta"] for c in pop)
    rng=random.Random(seed)
    names=("observed_equal_cluster","ipw_true_probability","ipw_misspecified")
    estimates={name:[] for name in names}
    ess_values=[]
    selected_counts=[]
    for _ in range(simulations):
        sample=[]
        for c in pop:
            pi=0.8 if c["delta"]>0 else 0.25
            if rng.random() < pi:
                pihat=min(1-min_probability,max(min_probability,_expit(_logit(pi)+logit_shift)))
                sample.append((c["delta"],pi,pihat))
        if len(sample)<2:
            continue
        ds=[x[0] for x in sample]
        wt=[1/x[1] for x in sample]
        wm=[1/x[2] for x in sample]
        estimates["observed_equal_cluster"].append(mean(ds))
        estimates["ipw_true_probability"].append(sum(d*w for d,w in zip(ds,wt))/sum(wt))
        estimates["ipw_misspecified"].append(sum(d*w for d,w in zip(ds,wm))/sum(wm))
        ess_values.append(sum(wm)**2/sum(w*w for w in wm))
        selected_counts.append(len(sample))
    n=len(estimates["observed_equal_cluster"])
    if n==0:
        raise RuntimeError("no simulation produced at least two selected clusters")
    results={}
    for name,vals in estimates.items():
        results[name]={"mean_estimate":mean(vals),"bias":mean(vals)-truth,
                       "rmse":math.sqrt(mean((x-truth)**2 for x in vals)),
                       "empirical_sd":pstdev(vals)}
    return {"synthetic_only":True,"selection_mechanism":"pi=.8 if delta>0 else .25",
            "n_clusters":n_clusters,"simulations_requested":simulations,
            "simulations_used":n,"seed":seed,"logit_shift":logit_shift,
            "true_equal_cluster_mean":truth,"mean_selected_clusters":mean(selected_counts),
            "mean_misspecified_weight_ess":mean(ess_values),"results":results,
            "limitations":[
                "Finite synthetic population; not evidence about a real study.",
                "True inclusion probabilities are known only because this is a simulation.",
                "IPW requires correct inclusion probabilities, positivity, and design assumptions.",
                "A sensitivity grid over plausible probabilities is preferable when the true design is unknown.",
                "No causal claim is implied."]}

if __name__ == "__main__":
    import json
    print(json.dumps(run_misspecification_test(),indent=2,sort_keys=True))
