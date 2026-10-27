#!/usr/bin/env python3
"""Finite-state contracts for effect/evidence and ledger/projection boundaries."""
import hashlib
import json
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
    ledger.add("event-a")
    writer_a_view.add("event-a")
    projection_after_a = writer_a_view.copy()
    ledger.add("event-b")
    writer_b_view.add("event-b")
    projection_after_b = writer_b_view.copy()
    assert projection_after_a == {"event-a"}
    return ledger, projection_after_b


def make_chain(events: list[dict]) -> list[dict]:
    rows = []
    previous = "0" * 64
    for event in events:
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"), default=str).encode()
        digest = hashlib.sha256(previous.encode() + canonical).hexdigest()
        rows.append({"event": event, "prev_digest": previous, "digest": digest})
        previous = digest
    return rows


def verify_model_chain(rows: list[dict]) -> bool:
    previous = "0" * 64
    for row in rows:
        if row["prev_digest"] != previous:
            return False
        canonical = json.dumps(row["event"], sort_keys=True, separators=(",", ":"), default=str).encode()
        expected = hashlib.sha256(previous.encode() + canonical).hexdigest()
        if expected != row["digest"]:
            return False
        previous = row["digest"]
    return True



def append_once_model(records: dict[str, dict], event_id: str, event: dict) -> tuple[dict, bool]:
    """Model stable-ID deduplication, ignoring attempt-local projection metadata."""
    logical = {
        key: value for key, value in event.items()
        if key not in {"_indexed_at", "_digest", "_prev_digest"}
    }
    if event_id in records:
        if records[event_id] != logical:
            raise ValueError("event ID reused with different payload")
        return dict(records[event_id]), True
    records[event_id] = dict(logical)
    return dict(logical), False


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

    # Integrity validates rows present; it does not prove projection completeness.
    expected_events = [{"event_id": "A", "value": 1}, {"event_id": "B", "value": 2}]
    valid_ledger = make_chain(expected_events)
    assert verify_model_chain(valid_ledger)
    projection_ids = {"B"}
    ledger_ids = {row["event"]["event_id"] for row in valid_ledger}
    assert ledger_ids == {"A", "B"}
    assert not ledger_ids.issubset(projection_ids)
    assert verify_model_chain(valid_ledger), "valid ledger chain must remain valid despite incomplete projection"
    # Removing the tail yields a valid prefix; the chain alone cannot detect truncation.
    truncated_prefix = valid_ledger[:1]
    assert verify_model_chain(truncated_prefix)
    assert len(truncated_prefix) < len(expected_events)


    # Stable event identity: repeated delivery returns the original logical
    # receipt, while reusing an ID for a different payload is rejected.
    event_records: dict[str, dict] = {}
    original, replayed = append_once_model(
        event_records, "evt-stable", {"event_id": "evt-stable", "value": 9, "_indexed_at": 1.0}
    )
    assert not replayed
    replay, replayed = append_once_model(
        event_records, "evt-stable", {"event_id": "evt-stable", "value": 9, "_indexed_at": 2.0}
    )
    assert replayed and replay == original
    assert len(event_records) == 1
    try:
        append_once_model(
            event_records, "evt-stable", {"event_id": "evt-stable", "value": 10}
        )
    except ValueError:
        pass
    else:
        raise AssertionError("same event ID with a different payload must fail")
    for _ in range(32):
        same, was_replay = append_once_model(
            event_records, "evt-race", {"event_id": "evt-race", "value": 11}
        )
    assert was_replay and same["value"] == 11
    assert len(event_records) == 2

    print("PASS effect/evidence: 8/8 states; ledger/projection: 16/16 states; stale-writer lost update reproduced; valid-chain/incomplete-projection and valid-prefix truncation; stable-ID replay/conflict checks verified")


if __name__ == "__main__":
    main()
