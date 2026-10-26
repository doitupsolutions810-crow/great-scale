#!/usr/bin/env python3
"""CLI: CI evidence must be fresh for the current PR/base/workflow snapshot."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Snapshot:
    head_sha: str
    base_sha: str
    workflow_sha: str
    candidate_sha: str
    run_head_sha: str
    run_base_sha: str
    run_workflow_sha: str
    run_candidate_sha: str
    run_id: str
    conclusion: str


def accept_current(e: Snapshot) -> bool:
    # Equality to the current snapshot is the freshness contract.
    # This model assumes the provider's candidate semantics have already been
    # established; it does not itself query GitHub or authenticate the fields.
    return (
        bool(e.head_sha)
        and bool(e.base_sha)
        and bool(e.workflow_sha)
        and bool(e.candidate_sha)
        and e.run_head_sha == e.head_sha
        and e.run_base_sha == e.base_sha
        and e.run_workflow_sha == e.workflow_sha
        and e.run_candidate_sha == e.candidate_sha
        and bool(e.run_id)
        and e.conclusion == "success"
    )


def good():
    return Snapshot("H1", "B1", "W1", "M1", "H1", "B1", "W1", "M1", "R1", "success")


def test_exact_snapshot_is_accepted():
    assert accept_current(good())


def test_head_or_base_movement_invalidates_old_evidence():
    e = good()
    assert not accept_current(Snapshot("H2", e.base_sha, e.workflow_sha, e.candidate_sha,
                                       e.run_head_sha, e.run_base_sha, e.run_workflow_sha,
                                       e.run_candidate_sha, e.run_id, e.conclusion))
    assert not accept_current(Snapshot(e.head_sha, "B2", e.workflow_sha, e.candidate_sha,
                                       e.run_head_sha, e.run_base_sha, e.run_workflow_sha,
                                       e.run_candidate_sha, e.run_id, e.conclusion))


def test_workflow_or_candidate_movement_invalidates_old_evidence():
    e = good()
    assert not accept_current(Snapshot(e.head_sha, e.base_sha, "W2", e.candidate_sha,
                                       e.run_head_sha, e.run_base_sha, e.run_workflow_sha,
                                       e.run_candidate_sha, e.run_id, e.conclusion))
    assert not accept_current(Snapshot(e.head_sha, e.base_sha, e.workflow_sha, "M2",
                                       e.run_head_sha, e.run_base_sha, e.run_workflow_sha,
                                       e.run_candidate_sha, e.run_id, e.conclusion))


def test_missing_or_non_success_run_is_rejected():
    e = good()
    assert not accept_current(Snapshot(e.head_sha, e.base_sha, e.workflow_sha, e.candidate_sha,
                                       e.run_head_sha, e.run_base_sha, e.run_workflow_sha,
                                       e.run_candidate_sha, "", e.conclusion))
    assert not accept_current(Snapshot(e.head_sha, e.base_sha, e.workflow_sha, e.candidate_sha,
                                       e.run_head_sha, e.run_base_sha, e.run_workflow_sha,
                                       e.run_candidate_sha, e.run_id, "failure"))


if __name__ == "__main__":
    test_exact_snapshot_is_accepted()
    test_head_or_base_movement_invalidates_old_evidence()
    test_workflow_or_candidate_movement_invalidates_old_evidence()
    test_missing_or_non_success_run_is_rejected()
    print("PASS CLI: CI evidence is accepted only for the exact current snapshot")
