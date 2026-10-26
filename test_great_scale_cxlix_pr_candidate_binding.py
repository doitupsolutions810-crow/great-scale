#!/usr/bin/env python3
"""CXLIX/CLXV: bind CI evidence to the current PR merge candidate and parents."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    head_sha: str
    base_sha: str
    tested_sha: str
    workflow_sha: str
    run_id: str
    conclusion: str
    tests_reachable: bool
    candidate_matches: bool
    mergeability: str
    merge_parent_base: str
    merge_parent_head: str


def accept(e, expected_head, expected_base, expected_candidate, expected_workflow):
    return (
        e.head_sha == expected_head
        and e.base_sha == expected_base
        and e.mergeability == "MERGEABLE"
        and e.merge_parent_base == expected_base
        and e.merge_parent_head == expected_head
        and e.tested_sha == expected_candidate
        and e.workflow_sha == expected_workflow
        and bool(e.run_id)
        and e.conclusion == "success"
        and e.tests_reachable
        and e.candidate_matches
    )


def test_candidate_evidence_requires_full_revision_tuple():
    good = Evidence("H1", "B1", "M1", "W1", "run-1", "success", True, True,
                    "MERGEABLE", "B1", "H1")
    assert accept(good, "H1", "B1", "M1", "W1")
    # Same head, changed base/candidate: the earlier green result is stale.
    assert not accept(good, "H1", "B2", "M2", "W1")
    assert not accept(good, "H1", "B1", "M2", "W1")
    assert not accept(good, "H1", "B1", "M1", "W2")


def test_incomplete_or_failed_evidence_is_not_accepted():
    good = Evidence("H1", "B1", "M1", "W1", "run-1", "success", True, True,
                    "MERGEABLE", "B1", "H1")
    assert not accept(Evidence("H1", "B1", "M1", "W1", "", "success", True, True,
                               "MERGEABLE", "B1", "H1"), "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", "W1", "run-1", "failure", True, True,
                               "MERGEABLE", "B1", "H1"), "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", "W1", "run-1", "success", False, True,
                               "MERGEABLE", "B1", "H1"), "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", "W1", "run-1", "success", True, False,
                               "MERGEABLE", "B1", "H1"), "H1", "B1", "M1", "W1")


def test_candidate_must_exist_before_its_evidence_can_authorize():
    conflicting = Evidence("H1", "B1", "", "W1", "", "success", False, False,
                          "CONFLICTING", "B1", "H1")
    unknown = Evidence("H1", "B1", "", "W1", "", "success", False, False,
                       "UNKNOWN", "", "")
    assert not accept(conflicting, "H1", "B1", "M1", "W1")
    assert not accept(unknown, "H1", "B1", "M1", "W1")


def test_stale_github_merge_ref_is_rejected_even_if_a_run_is_green():
    # Current head H2 differs from the head parent H1 of the fetched merge ref.
    stale = Evidence("H2", "B1", "M-old", "W1", "run-old", "success", True, True,
                     "MERGEABLE", "B1", "H1")
    assert not accept(stale, "H2", "B1", "M-old", "W1")


if __name__ == "__main__":
    test_candidate_evidence_requires_full_revision_tuple()
    test_incomplete_or_failed_evidence_is_not_accepted()
    test_candidate_must_exist_before_its_evidence_can_authorize()
    test_stale_github_merge_ref_is_rejected_even_if_a_run_is_green()
    print("PASS CXLIX/CLXV: candidate identity, existence, freshness, and evidence acceptance")
