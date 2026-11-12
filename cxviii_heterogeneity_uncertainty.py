"""CXVIII: cluster heterogeneity and uncertainty for paired binary outcomes."""
from __future__ import annotations
import math
import random
from collections import defaultdict
from statistics import mean, median, stdev
from typing import Any, Iterable, Mapping

def _binary(value: Any, field: str) -> int:
    if isinstance(value, bool):
        return int(value)
    if value in (0, 1):
        return int(value)
    raise ValueError(f"{field} must be binary (0/1 or bool)")

def _delta(rows: list[tuple[int, int]]) -> float:
    n = len(rows)
    pa = sum(a for a, _ in rows) / n
    pb = sum(b for _, b in rows) / n
    pab = sum(a*b for a, b in rows) / n
    return pab - pa*pb

def analyze_heterogeneity(records: Iterable[Mapping[str, Any]], *, reps: int = 5000,
                          alpha: float = 0.05, seed: int = 0,
                          min_clusters: int = 10) -> dict[str, Any]:
    """Summarize cluster excess and bootstrap equal-cluster mean.

    Resampling is over observed cluster-level excess values, not individual rows.
    The percentile interval is approximate and does not imply causality.
    """
    if not isinstance(reps, int) or reps < 100:
        raise ValueError("reps must be an integer >= 100")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be strictly between 0 and 1")
    if not isinstance(min_clusters, int) or min_clusters < 2:
        raise ValueError("min_clusters must be an integer >= 2")
    grouped: dict[str, list[tuple[int, int]]] = defaultdict(list)
    all_rows: list[tuple[int, int]] = []
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("each record must be a mapping")
        if "cluster_id" not in record or record["cluster_id"] is None or str(record["cluster_id"]) == "":
            raise ValueError("cluster_id must be non-empty")
        a, b = _binary(record.get("a"), "a"), _binary(record.get("b"), "b")
        grouped[str(record["cluster_id"])].append((a, b))
        all_rows.append((a, b))
    if not grouped:
        raise ValueError("records must contain at least one row")
    ids = sorted(grouped)
    deltas = [_delta(grouped[c]) for c in ids]
    sizes = [len(grouped[c]) for c in ids]
    k = len(ids)
    result: dict[str, Any] = {
        "n_rows": len(all_rows), "n_clusters": k,
        "cluster_sizes": {c: len(grouped[c]) for c in ids},
        "cluster_excess": {c: _delta(grouped[c]) for c in ids},
        "equal_cluster_mean_excess": mean(deltas),
        "median_cluster_excess": median(deltas),
        "sd_cluster_excess": stdev(deltas) if k > 1 else 0.0,
        "min_cluster_excess": min(deltas), "max_cluster_excess": max(deltas),
        "trial_weighted_pooled_excess": _delta(all_rows),
        "alpha": alpha, "bootstrap_reps": reps,
        "interval_method": "percentile bootstrap over cluster-level excess values",
        "interval": None, "status": "INSUFFICIENT_CLUSTERS",
        "limitations": [
            "Percentile interval is approximate and may be unreliable with few clusters or rare outcomes.",
            "Observed clusters must represent the target population of clusters.",
            "Descriptive dependence does not establish causality.",
            "Positive mean does not imply every cluster has positive excess."
        ]
    }
    if k < min_clusters:
        return result
    rng = random.Random(seed)
    boot = sorted(mean(deltas[rng.randrange(k)] for _ in range(k)) for _ in range(reps))
    def quantile(p: float) -> float:
        pos = (len(boot)-1)*p
        lo, hi = math.floor(pos), math.ceil(pos)
        return boot[lo] if lo == hi else boot[lo] + (boot[hi]-boot[lo])*(pos-lo)
    lower, upper = quantile(alpha/2), quantile(1-alpha/2)
    result["interval"] = [lower, upper]
    if lower > 0:
        result["status"] = "EVIDENCE_OF_POSITIVE_MEAN_CLUSTER_EXCESS"
    elif upper < 0:
        result["status"] = "EVIDENCE_OF_NEGATIVE_MEAN_CLUSTER_EXCESS"
    else:
        result["status"] = "INCONCLUSIVE"
    return result
