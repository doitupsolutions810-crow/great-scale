#!/usr/bin/env python3
"""CLVIII/CLXVII/CLXVIII: classify blockers and require designated test-step evidence."""
from dataclasses import dataclass
from enum import Enum
import re


class Decision(Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


EXPECTED_WORKFLOW_BLOB = "a" * 40
EXPECTED_TEST_STEP = "Run canonical aggregate"


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
    workflow_blob_sha: str = ""
    test_step_name: str = ""
    test_step_status: str = ""
    test_step_conclusion: str = ""


def classify(evidence: CiEvidence | None, *, head_sha: str, base_sha: str,
             workflow_blob_sha: str,
             workflow_path: str = ".github/workflows/ci.yml",
             expected_job_name: str = "test",
             expected_test_step_name: str = EXPECTED_TEST_STEP) -> Decision:
    """Fail closed unless exact candidate, workflow, and designated test step are evidenced."""
    if evidence is None:
        return Decision.UNKNOWN
    if (
        evidence.provider != "github_actions"
        or not evidence.run_id
        or evidence.head_sha != head_sha
        or evidence.base_sha != base_sha
        or evidence.workflow_path != workflow_path
        or not re.fullmatch(r"[0-9a-f]{40}", workflow_blob_sha)
        or evidence.workflow_blob_sha != workflow_blob_sha
        or evidence.event != "pull_request"
        or evidence.job_name != expected_job_name
        or evidence.status != "completed"
        or evidence.conclusion not in {
            "success", "failure", "cancelled", "timed_out", "action_required", "skipped"
        }
    ):
        return Decision.UNKNOWN

    billing_lock = "account is locked due to a billing issue" in evidence.blocker_reason.casefold()
    if evidence.conclusion == "failure" and evidence.step_count == 0 and billing_lock:
        return Decision.BLOCKED

    execution_observed = (
        bool(evidence.runner_name)
        and evidence.step_count is not None
        and evidence.step_count > 0
    )
    if not execution_observed:
        return Decision.UNKNOWN

    designated_step_observed = (
        evidence.test_step_name == expected_test_step_name
        and evidence.test_step_status == "completed"
        and evidence.test_step_conclusion in {"success", "failure"}
    )
    if not designated_step_observed:
        return Decision.UNKNOWN

    if evidence.conclusion == "failure" or evidence.test_step_conclusion == "failure":
        return Decision.FAIL
    if evidence.conclusion == "success" and evidence.test_step_conclusion == "success":
        return Decision.PASS
    return Decision.UNKNOWN


def classify_exact(evidence: CiEvidence | None) -> Decision:
    return classify(
        evidence,
        head_sha="head",
        base_sha="base",
        workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
    )


def test_no_run_is_unknown_not_pass_or_fail():
    assert classify_exact(None) is Decision.UNKNOWN


def test_green_external_status_is_unknown():
    external = CiEvidence(
        "vercel", "run-1", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success"
    )
    assert classify_exact(external) is Decision.UNKNOWN


def test_exact_executed_test_step_and_job_outcomes_are_distinguished():
    common = dict(
        provider="github_actions", run_id="run-1", head_sha="head", base_sha="base",
        workflow_path=".github/workflows/ci.yml", workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
        event="pull_request", status="completed", job_name="test",
        runner_name="ubuntu-latest", step_count=4,
        test_step_name=EXPECTED_TEST_STEP, test_step_status="completed",
    )
    success = CiEvidence(**common, conclusion="success", test_step_conclusion="success")
    failed_test = CiEvidence(**common, conclusion="failure", test_step_conclusion="failure")
    failed_job_after_test = CiEvidence(**common, conclusion="failure", test_step_conclusion="success")
    job_green_after_test_failure = CiEvidence(**common, conclusion="success", test_step_conclusion="failure")
    assert classify_exact(success) is Decision.PASS
    assert classify_exact(failed_test) is Decision.FAIL
    assert classify_exact(failed_job_after_test) is Decision.FAIL
    assert classify_exact(job_green_after_test_failure) is Decision.FAIL


def test_explicit_billing_lock_before_first_step_is_blocked_not_test_failure():
    blocked = CiEvidence(
        "github_actions", "40392042836", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "failure",
        job_name="test", runner_name="", step_count=0,
        blocker_reason="The job was not started because your account is locked due to a billing issue.",
        workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
    )
    assert classify_exact(blocked) is Decision.BLOCKED


def test_unexplained_zero_step_failure_is_unknown_not_test_failure():
    incomplete = CiEvidence(
        "github_actions", "run-2", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "failure",
        job_name="test", runner_name="", step_count=0,
        workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
    )
    assert classify_exact(incomplete) is Decision.UNKNOWN


def test_success_without_any_runner_execution_is_not_pass():
    skipped = CiEvidence(
        "github_actions", "run-3", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success",
        job_name="test", runner_name="", step_count=0,
        workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
    )
    assert classify_exact(skipped) is Decision.UNKNOWN


def test_setup_steps_without_the_designated_test_step_are_not_pass():
    setup_only = CiEvidence(
        "github_actions", "run-setup-only", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success",
        job_name="test", runner_name="ubuntu-latest", step_count=3,
        workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
    )
    assert classify_exact(setup_only) is Decision.UNKNOWN


def test_skipped_test_step_cannot_make_a_successful_job_pass():
    skipped_test = CiEvidence(
        "github_actions", "run-skipped-test", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success",
        job_name="test", runner_name="ubuntu-latest", step_count=3,
        workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
        test_step_name=EXPECTED_TEST_STEP, test_step_status="completed",
        test_step_conclusion="skipped",
    )
    assert classify_exact(skipped_test) is Decision.UNKNOWN


def test_workflow_blob_mismatch_is_unknown_even_if_job_and_test_step_are_green():
    changed_workflow = CiEvidence(
        "github_actions", "run-mutated-workflow", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success",
        job_name="test", runner_name="ubuntu-latest", step_count=4,
        workflow_blob_sha="b" * 40,
        test_step_name=EXPECTED_TEST_STEP, test_step_status="completed",
        test_step_conclusion="success",
    )
    assert classify_exact(changed_workflow) is Decision.UNKNOWN


def test_cancelled_or_timed_out_run_is_unknown():
    for conclusion in ("cancelled", "timed_out", "action_required", "skipped"):
        evidence = CiEvidence(
            "github_actions", "run-4", "head", "base",
            ".github/workflows/ci.yml", "pull_request", "completed", conclusion,
            job_name="test", runner_name="ubuntu-latest", step_count=4,
            workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
            test_step_name=EXPECTED_TEST_STEP, test_step_status="completed",
            test_step_conclusion="success",
        )
        assert classify_exact(evidence) is Decision.UNKNOWN


def test_stale_incomplete_or_wrong_job_run_is_unknown():
    common = dict(
        provider="github_actions", run_id="run-5", head_sha="head", base_sha="base",
        workflow_path=".github/workflows/ci.yml", workflow_blob_sha=EXPECTED_WORKFLOW_BLOB,
        event="pull_request", conclusion="success", job_name="test",
        runner_name="ubuntu-latest", step_count=4, status="completed",
        test_step_name=EXPECTED_TEST_STEP, test_step_status="completed",
        test_step_conclusion="success",
    )
    stale = CiEvidence(**{**common, "head_sha": "old-head"})
    incomplete = CiEvidence(**{**common, "status": "in_progress"})
    wrong_job = CiEvidence(**{**common, "job_name": "lint"})
    unnamed_job = CiEvidence(**{**common, "job_name": ""})
    assert classify_exact(stale) is Decision.UNKNOWN
    assert classify_exact(incomplete) is Decision.UNKNOWN
    assert classify_exact(wrong_job) is Decision.UNKNOWN
    assert classify_exact(unnamed_job) is Decision.UNKNOWN


if __name__ == "__main__":
    tests = [
        test_no_run_is_unknown_not_pass_or_fail,
        test_green_external_status_is_unknown,
        test_exact_executed_test_step_and_job_outcomes_are_distinguished,
        test_explicit_billing_lock_before_first_step_is_blocked_not_test_failure,
        test_unexplained_zero_step_failure_is_unknown_not_test_failure,
        test_success_without_any_runner_execution_is_not_pass,
        test_setup_steps_without_the_designated_test_step_are_not_pass,
        test_skipped_test_step_cannot_make_a_successful_job_pass,
        test_workflow_blob_mismatch_is_unknown_even_if_job_and_test_step_are_green,
        test_cancelled_or_timed_out_run_is_unknown,
        test_stale_incomplete_or_wrong_job_run_is_unknown,
    ]
    for test in tests:
        test()
    print(f"PASS CLXVIII runner, workflow, and test-step classification ({len(tests)}/{len(tests)} tests)")
