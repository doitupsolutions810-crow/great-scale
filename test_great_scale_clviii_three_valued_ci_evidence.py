#!/usr/bin/env python3
"""CLVIII/CLXVII: separate CI outcome from runner execution evidence."""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CiEvidence:
    provider: str
    run_id: str
    head_sha: str
    base_sha: str
    workflow_path: str
    event: str
    status: str
    conclusion: str
    job_name: str = ""
    runner_name: str = ""
    step_count: int | None = None
    blocker_reason: str = ""


def classify(evidence: CiEvidence | None, *, head_sha: str, base_sha: str,
             workflow_path: str = ".github/workflows/ci.yml",
             expected_job_name: str = "test") -> Decision:
    """Classify a designated CI job without treating orchestration failure as test failure."""
    # Missing, stale, incomplete, non-authoritative, or wrong-job evidence is UNKNOWN.
    if evidence is None:
        return Decision.UNKNOWN
    if (
        evidence.provider != "github_actions"
        or not evidence.run_id
        or evidence.head_sha != head_sha
        or evidence.base_sha != base_sha
        or evidence.workflow_path != workflow_path
        or evidence.event != "pull_request"
        or evidence.job_name != expected_job_name
        or evidence.status != "completed"
        or evidence.conclusion not in {"success", "failure", "cancelled", "timed_out", "action_required"}
    ):
        return Decision.UNKNOWN

    # This explicit provider annotation explains why GitHub marked a check failed
    # without allocating a runner or executing a test step.
    billing_lock = "account is locked due to a billing issue" in evidence.blocker_reason.casefold()
    if evidence.conclusion == "failure" and evidence.step_count == 0 and billing_lock:
        return Decision.BLOCKED

    # A conclusion without observed job execution is not evidence about test code.
    execution_observed = bool(evidence.runner_name) and evidence.step_count is not None and evidence.step_count > 0
    if not execution_observed:
        return Decision.UNKNOWN

    if evidence.conclusion == "success":
        return Decision.PASS
    if evidence.conclusion == "failure":
        return Decision.FAIL
    return Decision.UNKNOWN


def test_no_run_is_unknown_not_pass_or_fail():
    assert classify(None, head_sha="head", base_sha="base") is Decision.UNKNOWN


def test_green_external_status_is_unknown():
    external = CiEvidence(
        "vercel", "run-1", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success"
    )
    assert classify(external, head_sha="head", base_sha="base") is Decision.UNKNOWN


def test_exact_executed_success_and_failure_are_distinguished():
    common = dict(
        provider="github_actions", run_id="run-1", head_sha="head", base_sha="base",
        workflow_path=".github/workflows/ci.yml", event="pull_request", status="completed",
        job_name="test", runner_name="ubuntu-latest", step_count=4,
    )
    success = CiEvidence(**common, conclusion="success")
    failure = CiEvidence(**common, conclusion="failure")
    assert classify(success, head_sha="head", base_sha="base") is Decision.PASS
    assert classify(failure, head_sha="head", base_sha="base") is Decision.FAIL


def test_explicit_billing_lock_before_first_step_is_blocked_not_test_failure():
    blocked = CiEvidence(
        "github_actions", "40392042836", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "failure",
        job_name="test", runner_name="", step_count=0,
        blocker_reason="The job was not started because your account is locked due to a billing issue.",
    )
    assert classify(blocked, head_sha="head", base_sha="base") is Decision.BLOCKED


def test_unexplained_zero_step_failure_is_unknown_not_test_failure():
    incomplete = CiEvidence(
        "github_actions", "run-2", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "failure",
        job_name="test", runner_name="", step_count=0,
    )
    assert classify(incomplete, head_sha="head", base_sha="base") is Decision.UNKNOWN


def test_success_without_observed_execution_is_not_pass():
    skipped = CiEvidence(
        "github_actions", "run-3", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success",
        job_name="test", runner_name="", step_count=0,
    )
    assert classify(skipped, head_sha="head", base_sha="base") is Decision.UNKNOWN


def test_cancelled_or_timed_out_run_is_unknown():
    for conclusion in ("cancelled", "timed_out", "action_required"):
        evidence = CiEvidence(
            "github_actions", "run-4", "head", "base",
            ".github/workflows/ci.yml", "pull_request", "completed", conclusion,
            job_name="test", runner_name="ubuntu-latest", step_count=3,
        )
        assert classify(evidence, head_sha="head", base_sha="base") is Decision.UNKNOWN


def test_stale_incomplete_or_wrong_job_run_is_unknown():
    common = dict(
        provider="github_actions", run_id="run-5", head_sha="head", base_sha="base",
        workflow_path=".github/workflows/ci.yml", event="pull_request", conclusion="success",
        job_name="test", runner_name="ubuntu-latest", step_count=4,
    )
    stale = CiEvidence(**{**common, "head_sha": "old-head"}, status="completed")
    incomplete = CiEvidence(**common, status="in_progress")
    wrong_job = CiEvidence(**{**common, "job_name": "lint"}, status="completed")
    unnamed_job = CiEvidence(**{**common, "job_name": ""}, status="completed")
    assert classify(stale, head_sha="head", base_sha="base") is Decision.UNKNOWN
    assert classify(incomplete, head_sha="head", base_sha="base") is Decision.UNKNOWN
    assert classify(wrong_job, head_sha="head", base_sha="base") is Decision.UNKNOWN
    assert classify(unnamed_job, head_sha="head", base_sha="base") is Decision.UNKNOWN


if __name__ == "__main__":
    tests = [
        test_no_run_is_unknown_not_pass_or_fail,
        test_green_external_status_is_unknown,
        test_exact_executed_success_and_failure_are_distinguished,
        test_explicit_billing_lock_before_first_step_is_blocked_not_test_failure,
        test_unexplained_zero_step_failure_is_unknown_not_test_failure,
        test_success_without_observed_execution_is_not_pass,
        test_cancelled_or_timed_out_run_is_unknown,
        test_stale_incomplete_or_wrong_job_run_is_unknown,
    ]
    for test in tests:
        test()
    print(f"PASS CLXVII runner-block classification ({len(tests)}/{len(tests)} tests)")
