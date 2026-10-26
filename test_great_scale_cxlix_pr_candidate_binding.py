#!/usr/bin/env python3
"""CXLIX: bind PR verification to head, base, tested candidate, and workflow."""
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


def accept(e, expected_head, expected_base, expected_candidate, expected_workflow):
    return (
        e.head_sha == expected_head
        and e.base_sha == expected_base
        and e.tested_sha == expected_candidate
        and e.workflow_sha == expected_workflow
        and bool(e.run_id)
        and e.conclusion == "success"
        and e.tests_reachable
        and e.candidate_matches
    )


def test_candidate_evidence_requires_full_revision_tuple():
    good = Evidence("H1", "B1", "M1", "W1", "run-1", "success", True, True)
    assert accept(good, "H1", "B1", "M1", "W1")
    # Same head, changed base/candidate: the earlier green result is stale.
    assert not accept(good, "H1", "B2", "M2", "W1")
    assert not accept(good, "H1", "B1", "M2", "W1")
    assert not accept(good, "H1", "B1", "M1", "W2")


def test_incomplete_or_failed_evidence_is_not_accepted():
    good = Evidence("H1", "B1", "M1", "W1", "run-1", "success", True, True)
    assert not accept(Evidence("H1", "B1", "M1", "W1", "", "success", True, True),
                      "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", "W1", "run-1", "failure", True, True),
                      "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", "W1", "run-1", "success", False, True),
                      "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", "W1", "run-1", "success", True, False),
                      "H1", "B1", "M1", "W1")


if __name__ == "__main__":
    test_candidate_evidence_requires_full_revision_tuple()
    test_incomplete_or_failed_evidence_is_not_accepted()
    print("PASS CXLIX: PR candidate identity, freshness, and evidence acceptance")
