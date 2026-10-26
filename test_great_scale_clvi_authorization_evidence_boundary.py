#!/usr/bin/env python3
"""CLVI: distinguish evidence shape validation from authentic provider verification.

This module checks a contract only. It does not cryptographically authenticate
GitHub or prove that the caller's evidence object came from GitHub.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorizationEvidence:
    issuer: str
    authenticated: bool
    candidate_sha: str
    required_checks_passed: bool
    merge_queue_or_protection_enforced: bool


def evidence_satisfies_contract(evidence: AuthorizationEvidence,
                                expected_candidate_sha: str) -> bool:
    return (
        evidence.issuer == "github"
        and evidence.authenticated
        and evidence.candidate_sha == expected_candidate_sha
        and evidence.required_checks_passed
        and evidence.merge_queue_or_protection_enforced
    )


def test_bare_boolean_is_not_authorization_evidence():
    # A bare True carries no issuer, candidate identity, or provenance.
    assert not evidence_satisfies_contract(
        AuthorizationEvidence("", True, "", True, True), "candidate-1"
    )


def test_candidate_mismatch_rejects_otherwise_valid_shaped_evidence():
    evidence = AuthorizationEvidence(
        "github", True, "candidate-old", True, True
    )
    assert not evidence_satisfies_contract(evidence, "candidate-new")


def test_contract_requires_all_authorization_dimensions():
    evidence = AuthorizationEvidence(
        "github", True, "candidate-1", True, True
    )
    assert evidence_satisfies_contract(evidence, "candidate-1")
    assert not evidence_satisfies_contract(
        AuthorizationEvidence("github", True, "candidate-1", False, True),
        "candidate-1",
    )
    assert not evidence_satisfies_contract(
        AuthorizationEvidence("github", True, "candidate-1", True, False),
        "candidate-1",
    )


if __name__ == "__main__":
    tests = [
        test_bare_boolean_is_not_authorization_evidence,
        test_candidate_mismatch_rejects_otherwise_valid_shaped_evidence,
        test_contract_requires_all_authorization_dimensions,
    ]
    for test in tests:
        test()
    print(f"PASS CLVI evidence-shape contract ({len(tests)}/{len(tests)} tests)")
