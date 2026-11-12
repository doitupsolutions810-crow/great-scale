"""Model-set adequacy checks for Great Scale rung XCIII.

A checklist records coverage evidence; an optional omission-mass bound computes
a lower bound only under the explicitly stated mixture assumptions.
"""
from __future__ import annotations
import math
from typing import Mapping, Sequence

REQUIRED_ADEQUACY_FIELDS = (
    "decision_scope_defined",
    "alternatives_searched",
    "failure_modes_reviewed",
    "data_sources_documented",
    "independent_review_completed",
)

def assess_model_set_adequacy(evidence: Mapping[str, bool]) -> dict:
    """Return transparent checklist status; this is not a probability of coverage."""
    missing = [key for key in REQUIRED_ADEQUACY_FIELDS if key not in evidence]
    failed = [key for key in REQUIRED_ADEQUACY_FIELDS
              if key in evidence and evidence[key] is not True]
    if missing or failed:
        status = "ADEQUACY_NOT_ESTABLISHED"
    else:
        status = "CHECKLIST_COMPLETE_REQUIRES_JUSTIFICATION"
    return {
        "status": status,
        "missing_fields": missing,
        "failed_or_unconfirmed_fields": failed,
        "completed_count": sum(evidence.get(key) is True for key in REQUIRED_ADEQUACY_FIELDS),
        "required_count": len(REQUIRED_ADEQUACY_FIELDS),
        "interpretation": "Checklist completion documents review steps; it does not prove all plausible models were included.",
    }

def omission_adjusted_lower_bound(
    in_set_worst_case_value: float,
    omitted_mass_upper_bound: float,
    omitted_model_value_lower_bound: float,
) -> dict[str, float | str]:
    """Bound expected net value under a stated mixture/omission-mass assumption.

    Assumption: omitted-model probability mass q is in [0, eta], included-model
    net value is at least v, omitted-model net value is at least L, and v >= L.
    The conservative bound is (1-eta)*v + eta*L. This is not a worst-case
    guarantee over arbitrary omitted states unless the lower bound L is valid.
    """
    v = float(in_set_worst_case_value)
    eta = float(omitted_mass_upper_bound)
    lower = float(omitted_model_value_lower_bound)
    if not all(math.isfinite(x) for x in (v, eta, lower)):
        raise ValueError("inputs must be finite")
    if not 0.0 <= eta <= 1.0:
        raise ValueError("omitted_mass_upper_bound must be in [0, 1]")
    if lower > v:
        raise ValueError("omitted_model_value_lower_bound must not exceed in-set lower bound")
    bound = (1.0 - eta) * v + eta * lower
    return {
        "in_set_worst_case_value": v,
        "omitted_mass_upper_bound": eta,
        "omitted_model_value_lower_bound": lower,
        "omission_adjusted_lower_bound": bound,
        "recommendation": "MEASURE_UNDER_STATED_BOUND" if bound > 1e-12 else "NOT_CERTIFIED_BY_BOUND",
        "assumption_scope": "valid only if the omitted-mass and omitted-value bounds are justified",
    }
