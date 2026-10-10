"""CXIII: empirical co-failure dependence diagnostics from controlled trials."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
import math

def analyze_failure_trials(trials: Sequence[Mapping[str, Any]], observer_a: str, observer_b: str) -> dict[str, Any]:
    """Compute descriptive co-failure rates and independence benchmark.

    Each trial must contain boolean outcomes under 'failures', keyed by observer.
    This is descriptive; no causal or universal-independence claim is made.
    """
    if not observer_a or not observer_b or observer_a == observer_b:
        raise ValueError("two distinct non-empty observer IDs are required")
    if not trials:
        raise ValueError("at least one trial is required")
    pairs=[]
    for i, trial in enumerate(trials):
        failures=trial.get("failures")
        if not isinstance(failures, Mapping) or observer_a not in failures or observer_b not in failures:
            raise ValueError(f"trial {i} must include both observers")
        a,b=failures[observer_a],failures[observer_b]
        if not isinstance(a,bool) or not isinstance(b,bool):
            raise ValueError(f"trial {i} outcomes must be booleans")
        pairs.append((a,b))
    n=len(pairs)
    pa=sum(a for a,_ in pairs)/n
    pb=sum(b for _,b in pairs)/n
    joint=sum(a and b for a,b in pairs)/n
    excess=joint-pa*pb
    # Phi correlation is undefined when either variable has zero variance.
    p11=joint; p10=pa-joint; p01=pb-joint; p00=1-pa-pb+joint
    denom=math.sqrt(pa*(1-pa)*pb*(1-pb))
    phi=(excess/denom) if denom > 0 else None
    return {
        "observer_a":observer_a,"observer_b":observer_b,"trials":n,
        "failure_rate_a":pa,"failure_rate_b":pb,
        "joint_failure_rate":joint,
        "independence_benchmark":pa*pb,
        "excess_joint_failure":excess,
        "phi_correlation":phi,
        "contingency":{"both_fail":p11,"a_only_fail":p10,"b_only_fail":p01,"neither_fail":p00},
        "interpretation":"Descriptive sample statistic only. Positive excess joint failure is consistent with co-failure dependence; finite trials do not prove causation or independence."
    }

def analyze_domains(trials: Sequence[Mapping[str, Any]], domains: Mapping[str,str]) -> dict[str, Any]:
    """Compare pairwise observed co-failure diagnostics for declared same/different domains."""
    observers=sorted({o for t in trials for o in t.get("failures", {})})
    pairs=[]
    for i,a in enumerate(observers):
        for b in observers[i+1:]:
            result=analyze_failure_trials(trials,a,b)
            same=bool(domains.get(a)) and domains.get(a)==domains.get(b)
            pairs.append({"observer_a":a,"observer_b":b,"same_declared_domain":same,
                          "excess_joint_failure":result["excess_joint_failure"],
                          "phi_correlation":result["phi_correlation"],"trials":result["trials"]})
    same=[p["excess_joint_failure"] for p in pairs if p["same_declared_domain"]]
    different=[p["excess_joint_failure"] for p in pairs if not p["same_declared_domain"]]
    return {"pair_diagnostics":pairs,
            "mean_excess_same_domain":sum(same)/len(same) if same else None,
            "mean_excess_different_domain":sum(different)/len(different) if different else None,
            "scope_note":"Pairwise summaries are exploratory and may be unstable with few trials or many correlated pairs; no p-values or causal conclusions are produced."}
