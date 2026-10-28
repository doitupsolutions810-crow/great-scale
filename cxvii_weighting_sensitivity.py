"""CXVII: compare trial-weighted and equal-cluster-weighted dependence estimands."""
from __future__ import annotations
from collections import defaultdict
from typing import Any, Iterable, Mapping

def _excess(rows: list[tuple[bool, bool]]) -> float:
    if not rows:
        raise ValueError("cluster must contain at least one trial")
    n = len(rows)
    pa = sum(a for a, _ in rows) / n
    pb = sum(b for _, b in rows) / n
    pab = sum(a and b for a, b in rows) / n
    return pab - pa * pb

def analyze_weighting_sensitivity(trials: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Compare pooled excess with the unweighted mean of within-cluster excesses.

    Rows require a non-empty cluster_id and strict boolean a_failed/b_failed values.
    The cluster-weighted estimate targets the mean of observed cluster-specific
    excesses; it is not automatically an unbiased estimator for every population.
    """
    grouped: dict[str, list[tuple[bool, bool]]] = defaultdict(list)
    all_rows: list[tuple[bool, bool]] = []
    for i, trial in enumerate(trials):
        if not isinstance(trial, Mapping):
            raise ValueError(f"trial {i} must be a mapping")
        for key in ("cluster_id", "a_failed", "b_failed"):
            if key not in trial:
                raise ValueError(f"trial {i} must contain cluster_id, a_failed, and b_failed")
        cid, a, b = trial["cluster_id"], trial["a_failed"], trial["b_failed"]
        if not isinstance(cid, str) or not cid.strip():
            raise ValueError(f"trial {i} cluster_id must be a non-empty string")
        if not isinstance(a, bool) or not isinstance(b, bool):
            raise ValueError(f"trial {i} outcomes must be booleans")
        grouped[cid].append((a, b))
        all_rows.append((a, b))
    if not all_rows:
        raise ValueError("at least one trial is required")

    n, k = len(all_rows), len(grouped)
    pooled = _excess(all_rows)
    cluster_stats = []
    for cid, rows in grouped.items():
        pa = sum(a for a, _ in rows) / len(rows)
        pb = sum(b for _, b in rows) / len(rows)
        pab = sum(a and b for a, b in rows) / len(rows)
        cluster_stats.append({
            "cluster_id": cid, "n_trials": len(rows),
            "p_a": pa, "p_b": pb, "p_joint": pab,
            "excess_joint_failure": pab - pa * pb,
        })
    equal_cluster = sum(c["excess_joint_failure"] for c in cluster_stats) / k
    sizes = [len(grouped[cid]) for cid in grouped]
    discrepancy = equal_cluster - pooled
    return {
        "schema": "great-scale-cxvii-v1",
        "n_trials": n, "n_clusters": k,
        "cluster_size_summary": {"minimum": min(sizes), "maximum": max(sizes),
            "mean": n / k},
        "trial_weighted_excess": pooled,
        "equal_cluster_weighted_mean_excess": equal_cluster,
        "cluster_minus_trial_weighted_difference": discrepancy,
        "absolute_weighting_discrepancy": abs(discrepancy),
        "cluster_results": cluster_stats,
        "interpretation": [
            "Trial-weighted excess describes the pooled trial distribution.",
            "Equal-cluster-weighted mean excess gives each observed cluster equal weight.",
            "A discrepancy is an estimand/heterogeneity diagnostic, not automatically a bias estimate.",
            "Within-cluster excess may be unstable for small clusters and is not defined as population truth by this computation.",
            "Clusters should represent the population units relevant to the scientific question."
        ]
    }
