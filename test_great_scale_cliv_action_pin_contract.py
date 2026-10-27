#!/usr/bin/env python3
"""CLV: assert real CI workflow action uses are immutable, not just example strings."""
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
USES = re.compile(r"^\s*-\s+uses:\s*([^\s#]+)", re.MULTILINE)


def action_ref_is_immutable(reference: str) -> bool:
    action, sep, ref = reference.partition("@")
    return bool(sep and action and SHA.fullmatch(ref))


def test_full_commit_sha_is_accepted():
    assert action_ref_is_immutable(
        "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"
    )


def test_tags_and_branches_are_not_immutable_identity():
    for ref in (
        "actions/checkout@v4",
        "actions/setup-node@v4.2.2",
        "actions/setup-node@main",
        "actions/checkout@release/4.x",
        "",
    ):
        assert not action_ref_is_immutable(ref), ref


def test_actual_ci_workflow_uses_only_immutable_action_refs():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    refs = USES.findall(workflow)
    assert refs, "workflow has no action uses to validate"
    mutable = [ref for ref in refs if not action_ref_is_immutable(ref)]
    assert not mutable, f"mutable action references found: {mutable}"


if __name__ == "__main__":
    tests = [
        test_full_commit_sha_is_accepted,
        test_tags_and_branches_are_not_immutable_identity,
        test_actual_ci_workflow_uses_only_immutable_action_refs,
    ]
    for test in tests:
        test()
    print(f"PASS CLV: workflow action pin contract ({len(tests)}/{len(tests)} tests)")
