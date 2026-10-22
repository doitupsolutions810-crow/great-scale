"""CXV: cluster-aware bootstrap uncertainty for paired binary failure outcomes."""
from __future__ import annotations
import random
from typing import Any, Iterable, Mapping

def _quantile(values: list[float], p: float) -> float:
    pos = (len(values) - 1) * p
    lo = int(pos); hi = min(lo + 1, len(values) - 1); frac = pos - lo
    return values[lo] * (1 - frac) + values[hi] * frac

def _excess(rows: list[tuple[bool, bool]]) -> float:
    n = len(rows)
    pa = sum(a for a, _ in rows) / n
    pb = sum(b for _, b in rows) / n
    pab = sum(a and b for a, b in rows) / n
    return pab - pa * pb

def analyze_cluster_dependence(
    trials: Iterable[Mapping[str, Any]], *, bootstrap_replicates: int = 2000,
    alpha: float = 0.05, seed: int = 0, min_clusters: int = 10
) -> dict[str, Any]:
    """Bootstrap entire clusters, preserving all paired rows within each sampled cluster.

    Cluster identifiers must represent plausible independent sampling units.
    The pooled statistic is trial-weighted; unequal/informative cluster sizes can
    change its interpretation and should be analyzed separately.
    """
    if isinstance(bootstrap_replicates, bool) or not isinstance(bootstrap_replicates, int) or bootstrap_replicates < 100:
        raise ValueError("bootstrap_replicates must be an integer >= 100")
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    if isinstance(min_clusters, bool) or not isinstance(min_clusters, int) or min_clusters < 2:
        raise ValueError("min_clusters must be an integer >= 2")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    grouped: dict[str, list[tuple[bool, bool]]] = {}
    for i, trial in enumerate(trials):
        if not isinstance(trial, Mapping):
            raise ValueError(f"trial {i} must be a mapping")
        for field in ("cluster_id", "a_failed", "b_failed"):
            if field not in trial:
                raise ValueError(f"trial {i} must contain cluster_id, a_failed, and b_failed")
        cluster = trial["cluster_id"]
        a, b = trial["a_failed"], trial["b_failed"]
        if not isinstance(cluster, str) or not cluster.strip():
            raise ValueError(f"trial {i} cluster_id must be a non-empty string")
        if not isinstance(a, bool) or not isinstance(b, bool):
            raise ValueError(f"trial {i} outcomes must be booleans")
        grouped.setdefault(cluster, []).append((a, b))
    if not grouped:
        raise ValueError("at least one trial is required")

    clusters = list(grouped.values())
    rows = [row for cluster_rows in clusters for row in cluster_rows]
    estimate = _excess(rows)
    rng = random.Random(seed)
    boot: list[float] = []
    for _ in range(bootstrap_replicates):
        chosen = [clusters[rng.randrange(len(clusters))] for _ in range(len(clusters))]
        sample = [row for cluster_rows in chosen for row in cluster_rows]
        boot.append(_excess(sample))
    boot.sort()
    lower, upper = _quantile(boot, alpha / 2), _quantile(boot, 1 - alpha / 2)
    if len(clusters) < min_clusters:
        status = "INSUFFICIENT_CLUSTERS"
    elif lower > 0:
        status = "EVIDENCE_OF_POSITIVE_EXCESS"
    elif upper < 0:
        status = "EVIDENCE_OF_NEGATIVE_EXCESS"
    else:
        status = "INCONCLUSIVE"
    return {
        "schema": "great-scale-cxv-v1",
        "n_trials": len(rows),
        "n_clusters": len(clusters),
        "cluster_sizes": [len(cluster) for cluster in clusters],
        "bootstrap_replicates": bootstrap_replicates,
        "alpha": float(alpha),
        "seed": seed,
        "p_a": sum(a for a, _ in rows) / len(rows),
        "p_b": sum(b for _, b in rows) / len(rows),
        "p_joint": sum(a and b for a, b in rows) / len(rows),
        "excess_joint_failure": estimate,
        "interval_method": "cluster-resampled percentile bootstrap",
        "interval_lower": lower,
        "interval_upper": upper,
        "status": status,
        "limitations": [
            "Bootstrap interval is approximate and does not prove independence or dependence.",
            "Clusters must be defensible independent sampling units; shared dependence across clusters is not handled.",
            "Few clusters can make bootstrap intervals unreliable even with many trials.",
            "Pooled estimate is trial-weighted; informative unequal cluster sizes can change interpretation.",
            "Temporal dependence, rare events, adaptive collection, and multiple comparisons need further methods."
        ]
    }
