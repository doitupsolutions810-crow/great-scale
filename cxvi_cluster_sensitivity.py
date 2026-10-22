"""CXVI: sensitivity of dependence estimates to clustering assumptions."""
from __future__ import annotations
from collections import Counter
from math import sqrt
from typing import Any, Iterable, Mapping
from cxiv_uncertainty_aware_dependence import analyze_dependence
from cxv_cluster_aware_uncertainty import analyze_cluster_dependence

def analyze_cluster_sensitivity(trials: Iterable[Mapping[str, Any]], *,
    icc_values: Iterable[float] = (0.0, 0.1, 0.2, 0.5, 1.0),
    bootstrap_replicates: int = 2000, alpha: float = 0.05, seed: int = 0,
    min_clusters: int = 10, min_trials: int = 20) -> dict[str, Any]:
    """Compare row/cluster bootstrap and hypothetical ICC design-effect scenarios."""
    rows = list(trials)
    if not rows:
        raise ValueError("at least one trial is required")
    iccs = list(icc_values)
    if not iccs:
        raise ValueError("icc_values must contain at least one value")
    for rho in iccs:
        if isinstance(rho, bool) or not isinstance(rho, (int, float)) or not 0 <= rho <= 1:
            raise ValueError("each ICC value must be numeric and in [0, 1]")
    row = analyze_dependence(rows, bootstrap_replicates=bootstrap_replicates,
        alpha=alpha, seed=seed, min_trials=min_trials)
    cluster = analyze_cluster_dependence(rows, bootstrap_replicates=bootstrap_replicates,
        alpha=alpha, seed=seed, min_clusters=min_clusters)
    counts: Counter[str] = Counter()
    for i, trial in enumerate(rows):
        if not isinstance(trial, Mapping):
            raise ValueError(f"trial {i} must be a mapping")
        cid = trial.get("cluster_id")
        if not isinstance(cid, str) or not cid.strip():
            raise ValueError(f"trial {i} must contain a non-empty string cluster_id")
        counts[cid] += 1
    sizes = list(counts.values())
    n, k = len(rows), len(sizes)
    mean_size = n / k
    sd_size = sqrt(sum((m - mean_size) ** 2 for m in sizes) / k)
    cv = sd_size / mean_size if mean_size else 0.0
    scenarios = []
    for rho in iccs:
        deff = max(1.0, 1.0 + (((1.0 + cv * cv) * mean_size) - 1.0) * float(rho))
        scenarios.append({"assumed_icc": float(rho), "design_effect_approx": deff,
                          "effective_sample_size_approx": n / deff})
    rw = row["interval_upper"] - row["interval_lower"]
    cw = cluster["interval_upper"] - cluster["interval_lower"]
    return {
        "schema": "great-scale-cxvi-v1", "n_trials": n, "n_clusters": k,
        "cluster_size_summary": {"minimum": min(sizes), "maximum": max(sizes),
            "mean": mean_size, "population_sd": sd_size, "coefficient_of_variation": cv},
        "estimate_comparison": {"row_bootstrap_excess": row["excess_joint_failure"],
            "cluster_bootstrap_excess": cluster["excess_joint_failure"],
            "absolute_estimate_difference": abs(row["excess_joint_failure"] - cluster["excess_joint_failure"])},
        "interval_comparison": {
            "row_bootstrap": {"lower": row["interval_lower"], "upper": row["interval_upper"],
                "width": rw, "status": row["status"]},
            "cluster_bootstrap": {"lower": cluster["interval_lower"], "upper": cluster["interval_upper"],
                "width": cw, "status": cluster["status"]},
            "cluster_to_row_width_ratio": cw / rw if rw > 0 else None},
        "design_effect_sensitivity": scenarios,
        "interpretation": [
            "ICC values are hypothetical sensitivity inputs, not estimated from these outcomes.",
            "Effective sample size is a rough design-effect approximation, not a replacement for a valid cluster-aware interval.",
            "Row bootstrap assumes independent/exchangeable rows and is a contrast, not automatically endorsed.",
            "Cluster bootstrap requires clusters to be plausible independent sampling units.",
            "Different interval statuses indicate sensitivity to sampling assumptions and warrant investigation."
        ]
    }
