"""Great Scale XCV: evidence-gated admission of candidate models."""
from __future__ import annotations
import math
from typing import Mapping

REQUIRED_FIELDS = ("model_id", "assumptions", "construction_rationale", "evidence_reference")

def assess_candidate(candidate: Mapping) -> dict:
    """Separate stress-testing eligibility from admission to the plausible set."""
    missing = [k for k in REQUIRED_FIELDS if k not in candidate or candidate[k] in (None, "", [])]
    if missing:
        return {"status":"INCOMPLETE","stress_test":False,"admit_to_plausible_set":False,"missing_fields":missing,"reason":"Required construction or provenance fields are missing."}
    if candidate.get("contradicted_by_validation") is True:
        return {"status":"REJECTED_FOR_CURRENT_EVIDENCE","stress_test":True,"admit_to_plausible_set":False,"missing_fields":[],"reason":"Recorded validation contradicts this candidate; preserve it in the audit trail and revisit if evidence changes."}
    if candidate.get("independent_validation_passed") is True:
        return {"status":"ELIGIBLE_FOR_PLAUSIBLE_SET_ADMISSION","stress_test":True,"admit_to_plausible_set":True,"missing_fields":[],"reason":"Required metadata and independent validation are recorded; admission remains conditional on domain relevance and review of validation quality."}
    return {"status":"PENDING_INDEPENDENT_VALIDATION","stress_test":True,"admit_to_plausible_set":False,"missing_fields":[],"reason":"Candidate is suitable for exploratory stress tests but lacks independent validation for plausible-set admission."}

def decision_stability(current_values: Mapping[str, float], candidate_id: str, candidate_value: float, threshold: float = 0.0) -> dict:
    """Compute disposition before/after a candidate, independently of evidence status."""
    if not current_values:
        raise ValueError("current_values must not be empty")
    values = [float(v) for v in current_values.values()] + [float(candidate_value), float(threshold)]
    if any(not math.isfinite(v) for v in values):
        raise ValueError("all values and threshold must be finite")
    before = min(float(v) for v in current_values.values())
    after = min(before, float(candidate_value))
    d_before = "ACCEPT" if before > threshold else "NOT_CERTIFIED"
    d_after = "ACCEPT" if after > threshold else "NOT_CERTIFIED"
    return {"candidate_id":candidate_id,"current_worst_case":before,"expanded_worst_case":after,"decision_before":d_before,"decision_after":d_after,"decision_changed":d_before != d_after,"candidate_changes_worst_case":after < before,"interpretation":"Decision impact is separate from evidence quality; do not infer plausibility from a decision flip."}
