#!/usr/bin/env python3
"""CLIII: verification must still apply at the operation/merge boundary."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewState:
    head_sha: str
    base_sha: str
    workflow_sha: str
    candidate_sha: str


@dataclass(frozen=True)
class Verification:
    state: ReviewState
    run_id: str
    conclusion: str


def verified_for(state: ReviewState, evidence: Verification) -> bool:
    return (
        bool(evidence.run_id)
        and evidence.conclusion == "success"
        and evidence.state == state
    )


def may_merge(state_at_check: ReviewState, evidence: Verification,
              state_at_merge: ReviewState) -> bool:
    # A successful check is not a lease on future repository state.
    # Require state equality at the merge boundary or rerun/revalidate there.
    return (
        verified_for(state_at_check, evidence)
        and state_at_merge == state_at_check
    )


def test_unchanged_state_can_cross_merge_boundary():
    s = ReviewState("H1", "B1", "W1", "M1")
    e = Verification(s, "R1", "success")
    assert may_merge(s, e, s)


def test_base_advance_after_check_invalidates_merge_decision():
    checked = ReviewState("H1", "B1", "W1", "M1")
    evidence = Verification(checked, "R1", "success")
    merged_against = ReviewState("H1", "B2", "W1", "M2")
    assert verified_for(checked, evidence)
    assert not may_merge(checked, evidence, merged_against)


def test_head_or_workflow_change_after_check_invalidates_merge_decision():
    checked = ReviewState("H1", "B1", "W1", "M1")
    evidence = Verification(checked, "R1", "success")
    assert not may_merge(checked, evidence, ReviewState("H2", "B1", "W1", "M1"))
    assert not may_merge(checked, evidence, ReviewState("H1", "B1", "W2", "M1"))


def test_matching_state_but_failed_or_missing_run_is_rejected():
    s = ReviewState("H1", "B1", "W1", "M1")
    assert not may_merge(s, Verification(s, "", "success"), s)
    assert not may_merge(s, Verification(s, "R2", "failure"), s)


if __name__ == "__main__":
    tests = [
        test_unchanged_state_can_cross_merge_boundary,
        test_base_advance_after_check_invalidates_merge_decision,
        test_head_or_workflow_change_after_check_invalidates_merge_decision,
        test_matching_state_but_failed_or_missing_run_is_rejected,
    ]
    for test in tests:
        test()
    print(f"PASS CLIII: merge-boundary freshness contract ({len(tests)}/{len(tests)} tests)")
