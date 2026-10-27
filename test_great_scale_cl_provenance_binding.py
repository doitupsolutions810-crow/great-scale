#!/usr/bin/env python3
"""CL: reject self-asserted CI candidate matches; bind evidence to observed parents."""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Evidence:
    head_sha: str
    base_sha: str
    candidate_sha: str
    candidate_parent_shas: Tuple[str, ...]
    workflow_sha: str
    run_id: str
    conclusion: str
    tests_reachable: bool


def accept(e, expected_head, expected_base, expected_candidate, expected_workflow):
    # For a GitHub-style merge candidate, bind the observed candidate parents
    # to the immutable base/head tuple. Parent order is base, then PR head.
    return (
        e.head_sha == expected_head
        and e.base_sha == expected_base
        and e.candidate_sha == expected_candidate
        and e.candidate_parent_shas == (expected_base, expected_head)
        and e.workflow_sha == expected_workflow
        and bool(e.run_id)
        and e.conclusion == "success"
        and e.tests_reachable
    )


def test_acceptance_requires_candidate_and_parent_binding():
    good = Evidence("H1", "B1", "M1", ("B1", "H1"), "W1", "run-1", "success", True)
    assert accept(good, "H1", "B1", "M1", "W1")
    assert not accept(good, "H1", "B2", "M1", "W1")
    assert not accept(good, "H1", "B1", "M2", "W1")
    assert not accept(Evidence("H1", "B1", "M1", ("B1", "H2"), "W1", "run-1", "success", True),
                      "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", ("B2", "H1"), "W1", "run-1", "success", True),
                      "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", ("B1", "H1"), "W2", "run-1", "success", True),
                      "H1", "B1", "M1", "W1")


def test_missing_or_failed_run_evidence_is_rejected():
    base = Evidence("H1", "B1", "M1", ("B1", "H1"), "W1", "run-1", "success", True)
    assert not accept(Evidence("H1", "B1", "M1", ("B1", "H1"), "W1", "", "success", True),
                      "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", ("B1", "H1"), "W1", "run-1", "failure", True),
                      "H1", "B1", "M1", "W1")
    assert not accept(Evidence("H1", "B1", "M1", ("B1", "H1"), "W1", "run-1", "success", False),
                      "H1", "B1", "M1", "W1")


if __name__ == "__main__":
    test_acceptance_requires_candidate_and_parent_binding()
    test_missing_or_failed_run_evidence_is_rejected()
    print("PASS CL: candidate identity is bound to observed base/head parents and run evidence")
