"""Great Scale XCVI: validation leakage and evidence dependence checks."""
from __future__ import annotations
from collections import defaultdict
from typing import Mapping, Sequence

def assess_validation_independence(construction_sources: Sequence[str],
                                   validation_sources: Sequence[str],
                                   shared_data: bool = False,
                                   shared_preprocessing: bool = False,
                                   shared_selection_rule: bool = False) -> dict:
    """Detect documented overlap; this is a screening check, not proof of independence."""
    construction = set(construction_sources)
    validation = set(validation_sources)
    overlap = sorted(construction & validation)
    risks = []
    if overlap:
        risks.append("OVERLAPPING_SOURCE_IDENTIFIERS")
    if shared_data:
        risks.append("SHARED_DATA")
    if shared_preprocessing:
        risks.append("SHARED_PREPROCESSING")
    if shared_selection_rule:
        risks.append("SHARED_SELECTION_RULE")
    status = "DEPENDENCE_RISK_DETECTED" if risks else "NO_RECORDED_OVERLAP_REQUIRES_EXTERNAL_REVIEW"
    return {"status":status,"overlapping_sources":overlap,"risk_flags":risks,
            "construction_source_count":len(construction),"validation_source_count":len(validation),
            "warning":"No recorded overlap is not proof of independence; hidden dependencies and domain mismatch require review."}

def grouped_evidence_effective_sample_size(group_ids: Sequence[str]) -> dict:
    """Simple cluster count diagnostic; not a general ESS estimator."""
    n = len(group_ids)
    if n == 0:
        raise ValueError("group_ids must not be empty")
    groups = len(set(group_ids))
    return {"observations":n,"independent_groups":groups,
            "group_fraction":groups / n,
            "interpretation":"If observations within a group share a source or failure mechanism, the number of groups is a useful warning diagnostic, not a universally valid effective sample size."}

def admission_with_independence(candidate: Mapping, independence_report: Mapping) -> dict:
    """Gate admission when known dependence risks remain unresolved."""
    required = ("model_id", "assumptions", "construction_rationale", "evidence_reference")
    missing = [k for k in required if k not in candidate or candidate[k] in (None, "", [])]
    if missing:
        return {"status":"INCOMPLETE","admit":False,"missing_fields":missing}
    if independence_report.get("risk_flags"):
        return {"status":"VALIDATION_DEPENDENCE_REVIEW_REQUIRED","admit":False,
                "risk_flags":list(independence_report["risk_flags"])}
    if candidate.get("independent_validation_passed") is not True:
        return {"status":"INDEPENDENT_VALIDATION_NOT_CONFIRMED","admit":False,"risk_flags":[]}
    return {"status":"ELIGIBLE_PENDING_DOMAIN_REVIEW","admit":True,"risk_flags":[],
            "warning":"Eligibility is not automatic truth certification; inspect source independence, validation power, and domain match."}
