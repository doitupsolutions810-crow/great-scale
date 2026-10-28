"""Great Scale XCIV: structured discovery of decision-relevant alternatives."""
from __future__ import annotations
from typing import Mapping, Sequence

def decision_from_values(model_values: Mapping[str, float], threshold: float = 0.0) -> str:
    """Conservative decision based on minimum net value in the supplied set."""
    if not model_values:
        raise ValueError("model_values must not be empty")
    vals = [float(v) for v in model_values.values()]
    if any(v != v or v in (float("inf"), float("-inf")) for v in vals):
        raise ValueError("model values must be finite")
    return "ACCEPT" if min(vals) > threshold else "NOT_CERTIFIED"

def evaluate_model_expansion(
    current_values: Mapping[str, float],
    candidate_values: Mapping[str, float],
    threshold: float = 0.0,
) -> dict:
    """Compare current decision with decision after adding candidate models.

    Existing model values must remain unchanged. Candidates with duplicate IDs
    are treated as existing entries and must agree exactly; otherwise fail.
    """
    if not current_values:
        raise ValueError("current_values must not be empty")
    combined = dict(current_values)
    for model_id, value in candidate_values.items():
        if model_id in combined and float(combined[model_id]) != float(value):
            raise ValueError(f"existing model value changed for {model_id}")
        combined[model_id] = float(value)
    before_min = min(float(v) for v in current_values.values())
    after_min = min(combined.values())
    before_decision = decision_from_values(current_values, threshold)
    after_decision = decision_from_values(combined, threshold)
    return {
        "current_worst_case": before_min,
        "expanded_worst_case": after_min,
        "worst_case_change": after_min - before_min,
        "monotonicity_holds": after_min <= before_min,
        "decision_before": before_decision,
        "decision_after": after_decision,
        "decision_changed": before_decision != after_decision,
        "added_model_ids": sorted(set(candidate_values) - set(current_values)),
        "interpretation": "A candidate model is decision-relevant if it changes the disposition or tightens the worst-case value; plausibility still requires evidence.",
    }

def classify_candidate(candidate: Mapping) -> dict:
    """Separate a logically constructed counterexample from an evidence-backed one."""
    required = ("model_id", "assumptions", "construction_rationale", "evidence_reference")
    missing = [key for key in required if key not in candidate or candidate[key] in (None, "", [])]
    if missing:
        status = "INCOMPLETE_CANDIDATE"
    elif candidate.get("empirically_supported") is True:
        status = "EVIDENCE_BACKED_CANDIDATE_REQUIRES_VALIDATION"
    else:
        status = "HYPOTHETICAL_CANDIDATE_REQUIRES_EVIDENCE"
    return {
        "status": status,
        "missing_fields": missing,
        "decision_relevant": bool(candidate.get("decision_relevant", False)),
        "empirically_supported": candidate.get("empirically_supported") is True,
        "warning": "A counterexample's logical possibility does not establish its empirical plausibility.",
    }
