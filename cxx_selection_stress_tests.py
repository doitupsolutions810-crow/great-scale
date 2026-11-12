"""CXX: simulation-based stress tests for informative cluster size and selection.

Synthetic clusters have fixed paired binary outcomes, so each cluster's true
Delta is known. Repeated Bernoulli inclusion evaluates estimators against the
known finite-population equal-cluster mean. This is a diagnostic harness, not
a substitute for design-specific inference.
"""
from __future__ import annotations
import random
from statistics import mean, pstdev
from typing import Any

def _delta(rows: list[tuple[int,int]]) -> float:
    n=len(rows)
    pa=sum(a for a,_ in rows)/n
    pb=sum(b for _,b in rows)/n
    pab=sum(a*b for a,b in rows)/n
    return pab-pa*pb

def build_population(n_clusters: int = 200) -> list[dict[str, Any]]:
    """Create a deterministic finite population with varied sizes and effects."""
    if not isinstance(n_clusters,int) or n_clusters < 20:
        raise ValueError("n_clusters must be an integer >= 20")
    population=[]
    for g in range(n_clusters):
        # Two outcome patterns yield known contrast 0 or 0.25. Alternate blocks
        # so effect is not identical to size, then size can be stress-varied.
        dependent=(g % 4 in (2,3))
        size=4 if g%2==0 else 12
        pattern=[(0,0),(1,1)] if dependent else [(0,0),(0,1),(1,0),(1,1)]
        rows=[pattern[i%len(pattern)] for i in range(size)]
        population.append({"cluster_id":g,"rows":rows,"size":size,
                           "delta":_delta(rows)})
    return population

def _interval(values: list[float], reps: int, rng: random.Random) -> list[float]:
    n=len(values)
    boots=sorted(mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(reps))
    def q(p:float)->float:
        pos=(len(boots)-1)*p; lo=int(pos); hi=min(lo+1,len(boots)-1)
        return boots[lo]+(boots[hi]-boots[lo])*(pos-lo)
    return [q(.025),q(.975)]

def run_selection_stress_test(*, n_clusters:int=200, simulations:int=1000,
                              bootstrap_reps:int=500, seed:int=2026,
                              mechanism:str="size_correlated") -> dict[str,Any]:
    """Compare observed-cluster mean and IPW mean under known selection.

    mechanism is 'size_correlated' (larger clusters more likely selected) or
    'effect_correlated' (clusters with Delta=.25 more likely selected).
    Inverse-probability estimates use the true simulation inclusion probabilities.
    """
    if not isinstance(simulations,int) or simulations < 100:
        raise ValueError("simulations must be an integer >= 100")
    if not isinstance(bootstrap_reps,int) or bootstrap_reps < 100:
        raise ValueError("bootstrap_reps must be an integer >= 100")
    if mechanism not in ("size_correlated","effect_correlated"):
        raise ValueError("unknown selection mechanism")
    pop=build_population(n_clusters)
    truth=mean(c["delta"] for c in pop)
    rng=random.Random(seed)
    methods={"observed_equal_cluster":[],"ipw_hajek":[]}
    coverage={"observed_equal_cluster":0,"ipw_hajek":0}
    failures=0
    for _ in range(simulations):
        selected=[]
        for c in pop:
            if mechanism=="size_correlated":
                pi=0.25 if c["size"]==4 else 0.8
            else:
                pi=0.8 if c["delta"]>0 else 0.25
            if rng.random()<pi:
                selected.append((c,pi))
        if len(selected)<2:
            failures+=1
            continue
        d=[c["delta"] for c,_ in selected]
        w=[1.0/pi for _,pi in selected]
        est_obs=mean(d)
        est_ipw=sum(di*wi for di,wi in zip(d,w))/sum(w)
        methods["observed_equal_cluster"].append(est_obs)
        methods["ipw_hajek"].append(est_ipw)
        # Bootstrap intervals conditional on selected clusters. For IPW, use
        # weighted resampling approximation: resample clusters and retain weights.
        obs_rng=random.Random(rng.randrange(2**32))
        obs_ci=_interval(d,bootstrap_reps,obs_rng)
        ipw_rng=random.Random(rng.randrange(2**32))
        boot=[]
        for __ in range(bootstrap_reps):
            inds=[rng.randrange(len(d)) for ___ in range(len(d))]
            den=sum(w[i] for i in inds)
            boot.append(sum(d[i]*w[i] for i in inds)/den)
        boot.sort()
        ipw_ci=[boot[int(.025*(len(boot)-1))],boot[int(.975*(len(boot)-1))]]
        coverage["observed_equal_cluster"] += int(obs_ci[0] <= truth <= obs_ci[1])
        coverage["ipw_hajek"] += int(ipw_ci[0] <= truth <= ipw_ci[1])
    n=len(methods["observed_equal_cluster"])
    if n==0:
        raise RuntimeError("no simulation produced at least two selected clusters")
    summary={}
    for name, estimates in methods.items():
        summary[name]={
            "mean_estimate":mean(estimates),
            "bias":mean(estimates)-truth,
            "rmse":(mean((x-truth)**2 for x in estimates))**0.5,
            "empirical_sd":pstdev(estimates),
            "interval_coverage":coverage[name]/n
        }
    return {"synthetic_only":True,"mechanism":mechanism,"n_clusters":n_clusters,
            "simulations_requested":simulations,"simulations_used":n,
            "failed_too_few_selected":failures,"true_equal_cluster_mean":truth,
            "results":summary,
            "limitations":[
                "Finite synthetic population with deliberately simple outcome patterns.",
                "Selection probabilities are known by construction; real studies may not know them.",
                "Percentile/bootstrap coverage here is diagnostic and not guaranteed.",
                "The trial-weighted estimand is not the target in this harness.",
                "No causal claim is implied."
            ]}
