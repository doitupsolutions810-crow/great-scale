#!/usr/bin/env python3
"""Finite-state contract for effect/evidence atomicity boundaries."""
from itertools import product

STATES = tuple(product((False, True), repeat=3))
# (effect_may_have_occurred, evidence_durable, caller_saw_response)


def classify(effect_may_have_occurred: bool, evidence_durable: bool, caller_saw_response: bool) -> str:
    if effect_may_have_occurred and not evidence_durable:
        return "indeterminate"
    if effect_may_have_occurred and evidence_durable and caller_saw_response:
        return "complete"
    if effect_may_have_occurred and evidence_durable:
        return "reconcile_response"
    if not effect_may_have_occurred and not evidence_durable:
        return "not_committed"
    return "inconsistent"


def main() -> None:
    assert len(STATES) == 8
    for effect, durable, response in STATES:
        status = classify(effect, durable, response)
        if effect and not durable:
            assert status == "indeterminate"
            assert status != "failed_no_effect"
        if status == "complete":
            assert effect and durable and response
    assert classify(True, False, True) == "indeterminate"
    assert classify(True, False, False) == "indeterminate"
    assert classify(True, True, True) == "complete"
    print("PASS effect/evidence boundary: 8/8 states; effect-without-durable-evidence never clean failure")


if __name__ == "__main__":
    main()
