#!/usr/bin/env python3
"""CLXXIII: classify CI evidence without conflating runner startup with test outcome."""


def classify_run(status, conclusion, runner_id, executed_steps):
    """Return PASS, FAIL, or UNKNOWN from observed execution evidence."""
    if runner_id in (None, 0) or executed_steps == 0:
        return "UNKNOWN"
    if status == "completed" and conclusion == "success":
        return "PASS"
    if status == "completed" and conclusion == "failure":
        return "FAIL"
    return "UNKNOWN"


def test_runner_never_started_is_unknown():
    assert classify_run("completed", "failure", 0, 0) == "UNKNOWN"


def test_success_requires_observed_execution():
    assert classify_run("completed", "success", 123, 5) == "PASS"
    assert classify_run("completed", "success", 0, 0) == "UNKNOWN"


def test_executed_failure_is_failure():
    assert classify_run("completed", "failure", 123, 5) == "FAIL"


def test_in_progress_or_cancelled_without_execution_is_unknown():
    assert classify_run("in_progress", None, 123, 0) == "UNKNOWN"
    assert classify_run("completed", "cancelled", 123, 0) == "UNKNOWN"


if __name__ == "__main__":
    tests = [
        test_runner_never_started_is_unknown,
        test_success_requires_observed_execution,
        test_executed_failure_is_failure,
        test_in_progress_or_cancelled_without_execution_is_unknown,
    ]
    for test in tests:
        test()
    print(f"PASS CLXXIII CI evidence classification ({len(tests)}/{len(tests)} tests)")
