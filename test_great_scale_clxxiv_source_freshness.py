#!/usr/bin/env python3
"""CLXXIV: source freshness is distinct from client probe time and trust provenance."""
from datetime import datetime, timedelta, timezone

MAX_AGE = timedelta(minutes=5)
MAX_FUTURE_SKEW = timedelta(seconds=30)


def parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def freshness_failures(source_generated_at, source_expires_at, now,
                       max_age=MAX_AGE, max_future_skew=MAX_FUTURE_SKEW):
    """Model the v5.4.0 source-issued freshness contract; no source time means no pass."""
    generated = parse_time(source_generated_at)
    expires = parse_time(source_expires_at)
    if generated is None or expires is None:
        return {"timestamps-invalid"}

    failures = set()
    now = now.astimezone(timezone.utc)
    if generated > now + max_future_skew:
        failures.add("generated-in-future")
    if now - generated > max_age:
        failures.add("stale")
    if expires <= now:
        failures.add("expired")
    if expires <= generated or expires - generated > max_age:
        failures.add("lifetime-invalid")
    return failures


def test_fresh_source_window_is_accepted():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    generated = now - timedelta(seconds=5)
    expires = now + timedelta(seconds=90)
    assert freshness_failures(generated.isoformat(), expires.isoformat(), now) == set()


def test_client_probe_time_cannot_refresh_stale_source_document():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    generated = now - timedelta(minutes=6)
    expires = now + timedelta(seconds=30)
    failures = freshness_failures(generated.isoformat(), expires.isoformat(), now)
    assert "stale" in failures


def test_expired_source_evidence_is_rejected():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    generated = now - timedelta(minutes=1)
    expires = now - timedelta(seconds=1)
    assert "expired" in freshness_failures(generated.isoformat(), expires.isoformat(), now)


def test_future_source_generation_beyond_skew_is_rejected():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    generated = now + timedelta(minutes=1)
    expires = now + timedelta(minutes=2)
    assert "generated-in-future" in freshness_failures(generated.isoformat(), expires.isoformat(), now)


def test_missing_or_timezone_free_timestamps_fail_closed():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    assert freshness_failures(None, now.isoformat(), now) == {"timestamps-invalid"}
    assert "timestamps-invalid" in freshness_failures(
        "2026-10-27T00:00:00", "2026-10-27T00:01:00Z", now
    )


def test_overlong_source_validity_window_is_rejected():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    generated = now - timedelta(seconds=5)
    expires = generated + timedelta(minutes=10)
    assert "lifetime-invalid" in freshness_failures(
        generated.isoformat(), expires.isoformat(), now
    )


if __name__ == "__main__":
    tests = [
        test_fresh_source_window_is_accepted,
        test_client_probe_time_cannot_refresh_stale_source_document,
        test_expired_source_evidence_is_rejected,
        test_future_source_generation_beyond_skew_is_rejected,
        test_missing_or_timezone_free_timestamps_fail_closed,
        test_overlong_source_validity_window_is_rejected,
    ]
    for test_fn in tests:
        test_fn()
    print(f"PASS CLXXIV source freshness model ({len(tests)}/{len(tests)} tests)")
