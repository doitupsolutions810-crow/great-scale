#!/usr/bin/env python3
"""CLVII: distinguish a green external status from qualifying CI execution evidence."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CiRunEvidence:
    provider: str
    run_id: str
    head_sha: str
    base_sha: str
    workflow_path: str
    event: str
    status: str
    conclusion: str


def qualifies(e: CiRunEvidence, *, head_sha: str, base_sha: str,
              workflow_path: str = ".github/workflows/ci.yml") -> bool:
    return (
        e.provider == "github_actions"
        and bool(e.run_id)
        and e.head_sha == head_sha
        and e.base_sha == base_sha
        and e.workflow_path == workflow_path
        and e.event == "pull_request"
        and e.status == "completed"
        and e.conclusion == "success"
    )


def test_green_external_status_is_not_ci_run():
    external = CiRunEvidence(
        "vercel", "121836058727", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success"
    )
    assert not qualifies(external, head_sha="head", base_sha="base")


def test_exact_completed_pull_request_run_qualifies():
    run = CiRunEvidence(
        "github_actions", "4021", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success"
    )
    assert qualifies(run, head_sha="head", base_sha="base")


def test_missing_run_id_stale_head_and_wrong_base_rejected():
    good = CiRunEvidence(
        "github_actions", "4021", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "success"
    )
    assert not qualifies(CiRunEvidence(
        "github_actions", "", "head", "base", good.workflow_path,
        good.event, good.status, good.conclusion
    ), head_sha="head", base_sha="base")
    assert not qualifies(good, head_sha="new-head", base_sha="base")
    assert not qualifies(good, head_sha="head", base_sha="new-base")


def test_failed_or_wrong_event_run_rejected():
    failed = CiRunEvidence(
        "github_actions", "4021", "head", "base",
        ".github/workflows/ci.yml", "pull_request", "completed", "failure"
    )
    push = CiRunEvidence(
        "github_actions", "4022", "head", "base",
        ".github/workflows/ci.yml", "push", "completed", "success"
    )
    assert not qualifies(failed, head_sha="head", base_sha="base")
    assert not qualifies(push, head_sha="head", base_sha="base")


if __name__ == "__main__":
    tests = [
        test_green_external_status_is_not_ci_run,
        test_exact_completed_pull_request_run_qualifies,
        test_missing_run_id_stale_head_and_wrong_base_rejected,
        test_failed_or_wrong_event_run_rejected,
    ]
    for test in tests:
        test()
    print(f"PASS CLVII CI evidence classification ({len(tests)}/{len(tests)} tests)")
