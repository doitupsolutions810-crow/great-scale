"""CXIV: uncertainty-aware paired binary failure dependence."""
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

def analyze_dependence(trials: Iterable[Mapping[str, Any]], *, bootstrap_replicates: int = 2000,
                       alpha: float = 0.05, seed: int = 0, min_trials: int = 20) -> dict[str, Any]:
    """Paired-row percentile bootstrap CI for excess joint failure."""
    if isinstance(bootstrap_replicates, bool) or not isinstance(bootstrap_replicates, int) or bootstrap_replicates < 100:
        raise ValueError("bootstrap_replicates must be an integer >= 100")
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    if isinstance(min_trials, bool) or not isinstance(min_trials, int) or min_trials < 2:
        raise ValueError("min_trials must be an integer >= 2")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    rows = []
    for i, trial in enumerate(trials):
        if not isinstance(trial, Mapping):
            raise ValueError(f"trial {i} must be a mapping")
        if "a_failed" not in trial or "b_failed" not in trial:
            raise ValueError(f"trial {i} must contain a_failed and b_failed")
        a, b = trial["a_failed"], trial["b_failed"]
        if not isinstance(a, bool) or not isinstance(b, bool):
            raise ValueError(f"trial {i} outcomes must be booleans")
        rows.append((a, b))
    if not rows:
        raise ValueError("at least one trial is required")
    n = len(rows)
    pa = sum(a for a, _ in rows) / n
    pb = sum(b for _, b in rows) / n
    pab = sum(a and b for a, b in rows) / n
    estimate = pab - pa * pb
    rng = random.Random(seed)
    boot = []
    for _ in range(bootstrap_replicates):
        boot.append(_excess([rows[rng.randrange(n)] for _ in range(n)]))
    boot.sort()
    lower, upper = _quantile(boot, alpha / 2), _quantile(boot, 1 - alpha / 2)
    if n < min_trials:
        status = "INSUFFICIENT_DATA"
    elif lower > 0:
        status = "EVIDENCE_OF_POSITIVE_EXCESS"
    elif upper < 0:
        status = "EVIDENCE_OF_NEGATIVE_EXCESS"
    else:
        status = "INCONCLUSIVE"
    return {
        "schema": "great-scale-cxiv-v1", "n_trials": n,
        "bootstrap_replicates": bootstrap_replicates, "alpha": float(alpha), "seed": seed,
        "p_a": pa, "p_b": pb, "p_joint": pab, "excess_joint_failure": estimate,
        "interval_method": "paired-row percentile bootstrap", "interval_lower": lower,
        "interval_upper": upper, "status": status,
        "limitations": [
            "Bootstrap interval is approximate, not a proof.",
            "Assumes trial rows are exchangeable/independent for naive resampling.",
            "Rare events, small samples, clustering, temporal dependence, and multiple comparisons need special treatment.",
            "A confidence interval containing zero does not establish independence."
        ]
    }
