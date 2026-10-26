#!/usr/bin/env python3
"""CLIV: action references must be immutable to make workflow identity reproducible."""
import re


SHA = re.compile(r"^[0-9a-f]{40}$")


def action_ref_is_immutable(reference: str) -> bool:
    """A full commit SHA is immutable identity; tags/branches are movable names."""
    return bool(SHA.fullmatch(reference))


def test_full_commit_sha_is_accepted():
    assert action_ref_is_immutable("11bd71901bbe5b1630ceea73d27597364c9af683")


def test_tags_and_branches_are_not_immutable_identity():
    for ref in ("v4", "v4.2.2", "main", "release/4.x", ""):
        assert not action_ref_is_immutable(ref), ref


def test_near_sha_and_uppercase_are_rejected():
    assert not action_ref_is_immutable("11bd71901bbe5b1630ceea73d27597364c9af68")
    assert not action_ref_is_immutable("11BD71901BBE5B1630CEEA73D27597364C9AF683")


if __name__ == "__main__":
    tests = [
        test_full_commit_sha_is_accepted,
        test_tags_and_branches_are_not_immutable_identity,
        test_near_sha_and_uppercase_are_rejected,
    ]
    for test in tests:
        test()
    print(f"PASS CLIV: immutable action-reference contract ({len(tests)}/{len(tests)} tests)")
