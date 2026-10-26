#!/usr/bin/env python3
"""CLIX: server-side policy is a separately verified prerequisite, not a local claim."""
from enum import Enum


class PolicyState(Enum):
    ENFORCED = "enforced"
    NOT_ENFORCED = "not_enforced"
    UNKNOWN = "unknown"


def may_merge(ci_passed: bool, policy: PolicyState, candidate_bound: bool) -> bool:
    return ci_passed and policy is PolicyState.ENFORCED and candidate_bound


def test_unverified_policy_blocks_even_when_ci_passes():
    assert not may_merge(True, PolicyState.UNKNOWN, True)


def test_explicitly_disabled_policy_blocks_even_when_ci_passes():
    assert not may_merge(True, PolicyState.NOT_ENFORCED, True)


def test_enforced_policy_still_requires_ci_and_candidate_binding():
    assert may_merge(True, PolicyState.ENFORCED, True)
    assert not may_merge(False, PolicyState.ENFORCED, True)
    assert not may_merge(True, PolicyState.ENFORCED, False)


if __name__ == "__main__":
    tests = [
        test_unverified_policy_blocks_even_when_ci_passes,
        test_explicitly_disabled_policy_blocks_even_when_ci_passes,
        test_enforced_policy_still_requires_ci_and_candidate_binding,
    ]
    for test in tests:
        test()
    print(f"PASS CLIX server-policy gate ({len(tests)}/{len(tests)} tests)")
