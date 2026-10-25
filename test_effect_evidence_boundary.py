#!/usr/bin/env python3
"""Finite-state contracts for effect/evidence and ledger/projection boundaries."""
from itertools import product


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
    return effect_may_have_occurred and evidence_durable


def retry_is_safe(operation_committed: bool, idempotency_enforced: bool) -> bool:
    return not operation_committed or idempotency_enforced


def projection_state(ledger_committed: bool, projection_durable: bool, caller_acknowledged: bool) -> str:
    if ledger_committed and not projection_durable:
        return "reconcile_projection"
    if ledger_committed and projection_durable and caller_acknowledged:
        return "complete"
    if not ledger_committed and not projection_durable:
        return "not_committed"
    return "reconcile_acknowledgement"


def projection_retry_is_safe(ledger_committed: bool, idempotency_enforced: bool) -> bool:
    return not ledger_committed or idempotency_enforced


def stale_projection_interleaving() -> tuple[set[str], set[str]]:
    """Model two independently loaded writers replacing a JSON projection."""
    initial: set[str] = set()
    writer_a_view = initial.copy()
    writer_b_view = initial.copy()
    ledger: set[str] = set()

    # Both independent stores append to the authoritative ledger.
    ledger.add("event-a")
    writer_a_view.add("event-a")
    projection_after_a = writer_a_view.copy()

    ledger.add("event-b")
    writer_b_view.add("event-b")
    # B atomically replaces the file with a view derived from stale initial state.
    projection_after_b = writer_b_view.copy()
    assert projection_after_a == {"event-a"}
    return ledger, projection_after_b


def main() -> None:
    states = tuple(product((False, True), repeat=3))
    assert len(states) == 8
    for effect, durable, response in states:
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
    assert not retry_is_safe(True, False)
    assert retry_is_safe(True, True)
    assert retry_is_safe(False, False)

    projection_states = tuple(product((False, True), repeat=4))
    assert len(projection_states) == 16
    for ledger, projection, acknowledged, deduplicated in projection_states:
        status = projection_state(ledger, projection, acknowledged)
        if ledger and not projection:
            assert status == "reconcile_projection"
            assert status != "complete"
        if status == "complete":
            assert ledger and projection and acknowledged
        assert projection_retry_is_safe(not ledger, deduplicated) or not ledger
        if ledger and not deduplicated:
            assert not projection_retry_is_safe(ledger, deduplicated)

    assert projection_state(True, False, False) == "reconcile_projection"
    assert projection_state(True, True, True) == "complete"
    assert not projection_retry_is_safe(True, False)
    assert projection_retry_is_safe(True, True)

    ledger, projection = stale_projection_interleaving()
    assert ledger == {"event-a", "event-b"}
    assert projection == {"event-b"}
    assert not ledger.issubset(projection), "model must expose stale-writer lost update"

    print("PASS effect/evidence: 8/8 states; ledger/projection: 16/16 states; stale-writer counterexample reproduced")


if __name__ == "__main__":
    main()
