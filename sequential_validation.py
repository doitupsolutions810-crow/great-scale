"""Auditable utilities for repeated model evaluation.

These helpers quantify a narrow multiple-testing risk and flag when a final
test set has been used to guide a model decision. They do not estimate general
machine-learning selection bias or establish statistical validity by themselves.
"""
from __future__ import annotations

import math
from typing import Iterable, Mapping, Any


def _validate_probability(alpha: float) -> None:
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
        raise TypeError("alpha must be a number")
    if not math.isfinite(alpha) or not 0 <= alpha <= 1:
        raise ValueError("alpha must be finite and between 0 and 1 inclusive")


def _validate_looks(number_of_looks: int) -> None:
    if isinstance(number_of_looks, bool) or not isinstance(number_of_looks, int):
        raise TypeError("number_of_looks must be an integer")
    if number_of_looks < 1:
        raise ValueError("number_of_looks must be at least 1")


def familywise_false_positive_independent(
    alpha_per_test: float, number_of_looks: int
) -> float:
    """Exact probability of >=1 false positive for independent null tests."""
    _validate_probability(alpha_per_test)
    _validate_looks(number_of_looks)
    return 1.0 - (1.0 - alpha_per_test) ** number_of_looks


def bonferroni_alpha(alpha_total: float, number_of_looks: int) -> float:
    """Per-test level sufficient for familywise error <= alpha_total."""
    _validate_probability(alpha_total)
    _validate_looks(number_of_looks)
    return alpha_total / number_of_looks


def validation_set_status(
    look_count: int,
    test_used_for_tuning: bool,
    untouched_final_test: bool,
) -> str:
    """Return a conservative status label, not a statistical certification."""
    _validate_looks(look_count)
    if not isinstance(test_used_for_tuning, bool):
        raise TypeError("test_used_for_tuning must be bool")
    if not isinstance(untouched_final_test, bool):
        raise TypeError("untouched_final_test must be bool")
    if test_used_for_tuning:
        return "TEST_SET_COMPROMISED"
    if untouched_final_test:
        return "UNTOUCHED_FINAL_TEST"
    if look_count > 1:
        return "VALIDATION_REUSED"
    return "SINGLE_LOOK_NOT_FINAL"


def audit_model_selection(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Audit an event log for missing look indices and final-test contamination.

    Each event should contain an integer 'look', a 'dataset_role' of
    'validation' or 'test', and a boolean 'influenced_decision'.
    """
    rows = list(events)
    if not rows:
        raise ValueError("events must contain at least one event")
    seen_looks: set[int] = set()
    issues: list[str] = []
    test_influenced = False
    validation_looks = 0
    for index, event in enumerate(rows):
        look = event.get("look")
        role = event.get("dataset_role")
        influenced = event.get("influenced_decision")
        if isinstance(look, bool) or not isinstance(look, int) or look < 1:
            issues.append(f"event {index}: invalid look index")
        else:
            if look in seen_looks:
                issues.append(f"event {index}: duplicate look index {look}")
            seen_looks.add(look)
        if role not in {"validation", "test"}:
            issues.append(f"event {index}: invalid dataset_role")
        if not isinstance(influenced, bool):
            issues.append(f"event {index}: influenced_decision must be bool")
        elif role == "test" and influenced:
            test_influenced = True
        if role == "validation":
            validation_looks += 1
    if test_influenced:
        status = "TEST_SET_COMPROMISED"
    elif validation_looks > 1:
        status = "VALIDATION_REUSED_FINAL_TEST_NOT_SHOWN_COMPROMISED"
    else:
        status = "NO_TEST_CONTAMINATION_RECORDED"
    return {
        "status": status,
        "event_count": len(rows),
        "validation_look_count": validation_looks,
        "test_set_compromised": test_influenced,
        "issues": issues,
    }
