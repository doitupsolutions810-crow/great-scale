#!/usr/bin/env python3
"""CLVIII: preserve the difference between failed verification and absent evidence."""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    PASS = "pass"
    FAIL = "fail"
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


def classify(evidence: CiEvidence | None, *, head_sha: str, base_sha: str,
             workflow_path: str = ".github/workflows/ci.yml") -> Decision:
    # Missing, stale, incomplete, or non-authoritative evidence is UNKNOWN.
    # Only a qualifying completed GitHub Actions run can establish PASS or FAIL.
    if evidence is None:
        return Decision.UNKNOWN
    if (
        evidence.provider != "github_actions"
        or not evidence.run_id
        or evidence.head_sha != head_sha
        or evidence.base_sha != base_sha
        or evidence.workflow_path != workflow_path
        or evidence.event != "pull_request"
        or evidence.status != "completed"
        or evidence.conclusion not in {"success", "failure", "cancelled", "timed_out", "action_required"}
    ):
        return Decision.UNKNOWN
    return Decision.PASS if evidence.conclusion == "success" else Decision.FAIL


def test_no_run_is_unknown_not_pass_or_fail():
    assert classify(None, head_sha="head", base_sha="base") is Decision.UNKNOWN


def test_green_external_status_is_unknown():
    external = CiEvidence(
        "vercel", "run-1", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success"
    )
    assert classify(external, head_sha="head", base_sha="base") is Decision.UNKNOWN


def test_exact_success_is_pass_and_exact_failure_is_fail():
    common = dict(
        provider="github_actions", run_id="run-1", head_sha="head", base_sha="base",
        workflow_path=".github/workflows/ci.yml", event="pull_request", status="completed"
    )
    success = CiEvidence(**common, conclusion="success")
    failure = CiEvidence(**common, conclusion="failure")
    assert classify(success, head_sha="head", base_sha="base") is Decision.PASS
    assert classify(failure, head_sha="head", base_sha="base") is Decision.FAIL


def test_stale_or_incomplete_run_is_unknown():
    stale = CiEvidence(
        "github_actions", "run-1", "old-head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success"
    )
    incomplete = CiEvidence(
        "github_actions", "run-2", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "in_progress", "success"
    )
    assert classify(stale, head_sha="head", base_sha="base") is Decision.UNKNOWN
    assert classify(incomplete, head_sha="head", base_sha="base") is Decision.UNKNOWN


if __name__ == "__main__":
    tests = [
        test_no_run_is_unknown_not_pass_or_fail,
        test_green_external_status_is_unknown,
        test_exact_success_is_pass_and_exact_failure_is_fail,
        test_stale_or_incomplete_run_is_unknown,
    ]
    for test in tests:
        test()
    print(f"PASS CLVIII three-valued CI evidence logic ({len(tests)}/{len(tests)} tests)")
