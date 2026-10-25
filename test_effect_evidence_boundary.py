#!/usr/bin/env python3
"""Finite-state contracts for effect/evidence and ledger/projection boundaries."""
from itertools import product

STATES = tuple(product((False, True), repeat=3))
# (effect_may_have_occurred, evidence_durable, caller_saw_success_response)


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


def evidence_backed_success_allowed(effect_may_have_occurred: bool, evidence_durable: bool) -> bool:
    """Evidence-backed completion requires confirmed effect and durable evidence."""
    return effect_may_have_occurred and evidence_durable


def retry_is_safe(operation_committed: bool, idempotency_enforced: bool) -> bool:
    """A retry after an uncertain commit is safe only with deduplication."""
    return not operation_committed or idempotency_enforced


def projection_state(ledger_committed: bool, projection_durable: bool, caller_acknowledged: bool) -> str:
    """A separate projection is not complete merely because the ledger committed."""
    if ledger_committed and not projection_durable:
        return "reconcile_projection"
    if ledger_committed and projection_durable and caller_acknowledged:
        return "complete"
    if not ledger_committed and not projection_durable:
        return "not_committed"
    return "reconcile_acknowledgement"


def projection_retry_is_safe(ledger_committed: bool, idempotency_enforced: bool) -> bool:
    return not ledger_committed or idempotency_enforced


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

    for effect, durable in product((False, True), repeat=2):
        if not durable:
            assert not evidence_backed_success_allowed(effect, durable)
    assert evidence_backed_success_allowed(True, True)

    assert not retry_is_safe(operation_committed=True, idempotency_enforced=False)
    assert retry_is_safe(operation_committed=True, idempotency_enforced=True)
    assert retry_is_safe(operation_committed=False, idempotency_enforced=False)

    projection_states = tuple(product((False, True), repeat=4))
    assert len(projection_states) == 16
    for ledger, projection, acknowledged, deduplicated in projection_states:
        status = projection_state(ledger, projection, acknowledged)
        if ledger and not projection:
            assert status == "reconcile_projection"
            assert status != "complete"
        if status == "complete":
            assert ledger and projection and acknowledged
        if ledger and not deduplicated:
            assert not projection_retry_is_safe(ledger, deduplicated)
        else:
            assert projection_retry_is_safe(ledger, deduplicated)

    assert projection_state(True, False, False) == "reconcile_projection"
    assert projection_state(True, True, True) == "complete"
    assert not projection_retry_is_safe(ledger_committed=True, idempotency_enforced=False)
    assert projection_retry_is_safe(ledger_committed=True, idempotency_enforced=True)
    print("PASS effect/evidence: 8/8 states; ledger/projection: 16/16 states; retry requires deduplication after commit")


if __name__ == "__main__":
    main()
