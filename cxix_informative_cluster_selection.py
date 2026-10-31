"""CXIX: diagnostics for informative cluster size and observed-cluster selection."""
from __future__ import annotations
from collections import defaultdict
from math import sqrt
from statistics import mean
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

def _pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2:
        return None
    mx, my = mean(x), mean(y)
    dx, dy = [v-mx for v in x], [v-my for v in y]
    denom = sqrt(sum(v*v for v in dx) * sum(v*v for v in dy))
    return None if denom == 0 else sum(a*b for a,b in zip(dx,dy))/denom

def diagnose_cluster_size(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Report size/dependence association and separate selection-identifiability.

    Optional selection_probability must be constant within a cluster and lie in
    (0, 1]. If supplied for every observed cluster, report a Hájek-style
    inverse-probability weighted mean of cluster deltas. This only has a target
    interpretation if probabilities are valid and selection is ignorable given
    the design variables; observed rows alone cannot verify those assumptions.
    """
    grouped: dict[str, list[tuple[int,int]]] = defaultdict(list)
    probabilities: dict[str, float] = {}
    prob_presence: dict[str, bool] = {}
    for rec in records:
        if not isinstance(rec, Mapping):
            raise ValueError("each record must be a mapping")
        cid = rec.get("cluster_id")
        if cid is None or str(cid) == "":
            raise ValueError("cluster_id must be non-empty")
        cid = str(cid)
        a, b = _binary(rec.get("a"), "a"), _binary(rec.get("b"), "b")
        grouped[cid].append((a,b))
        p = rec.get("selection_probability")
        if p is None:
            prob_presence[cid] = False
        else:
            if isinstance(p, bool) or not isinstance(p, (int,float)) or not (0 < p <= 1):
                raise ValueError("selection_probability must be numeric in (0, 1]")
            p = float(p)
            if cid in probabilities and probabilities[cid] != p:
                raise ValueError("selection_probability must be constant within a cluster")
            probabilities[cid] = p
            prob_presence[cid] = True
    if not grouped:
        raise ValueError("records must contain at least one row")
    ids = sorted(grouped)
    sizes = [len(grouped[c]) for c in ids]
    deltas = [_delta(grouped[c]) for c in ids]
    size_corr = _pearson([float(v) for v in sizes], deltas)
    all_rows = [r for c in ids for r in grouped[c]]
    pooled = _delta(all_rows)
    equal_mean = mean(deltas)
    all_probs = all(prob_presence.get(c, False) and c in probabilities for c in ids)
    result: dict[str, Any] = {
        "n_clusters": len(ids),
        "cluster_sizes": {c: len(grouped[c]) for c in ids},
        "cluster_excess": {c: _delta(grouped[c]) for c in ids},
        "equal_cluster_mean_excess": equal_mean,
        "trial_weighted_pooled_excess": pooled,
        "size_excess_pearson_correlation": size_corr,
        "size_association_status": (
            "UNDEFINED_CONSTANT_SIZE_OR_EXCESS" if size_corr is None
            else "DIAGNOSTIC_ASSOCIATION_PRESENT" if abs(size_corr) >= 0.5
            else "NO_STRONG_LINEAR_ASSOCIATION_DETECTED"
        ),
        "selection_status": "PROBABILITIES_SUPPLIED_UNVERIFIED" if all_probs else "NOT_IDENTIFIABLE_FROM_OBSERVED_CLUSTERS_ALONE",
        "selection_weighted_mean_excess": None,
        "limitations": [
            "Size correlation is descriptive and can be unstable with few clusters.",
            "A weak Pearson correlation does not rule out nonlinear association or informative size.",
            "Selection probabilities must come from a defensible sampling design; supplying values does not validate them.",
            "Inverse-probability weighting cannot repair unmeasured selection mechanisms without additional assumptions."
        ]
    }
    if all_probs:
        weights = [1.0 / probabilities[c] for c in ids]
        result["selection_weighted_mean_excess"] = sum(w*d for w,d in zip(weights,deltas))/sum(weights)
    return result
