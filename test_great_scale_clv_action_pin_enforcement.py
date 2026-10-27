#!/usr/bin/env python3
"""CLV: enforce immutable action references in the actual CI workflow."""
from pathlib import Path
import re
import sys

USES = re.compile(r"^\s*-\s*uses:\s*([^@\s]+)@([^\s#]+)", re.MULTILINE)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def mutable_action_refs(workflow: str):
    """Return action references that are not full lowercase commit SHAs."""
    bad = []
    for match in USES.finditer(workflow):
        repository, ref = match.groups()
        if not SHA40.fullmatch(ref):
            bad.append((repository, ref))
    return bad


def test_policy_accepts_pinned_refs_and_rejects_tags():
    pinned = """
steps:
  - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
  - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020
"""
    assert mutable_action_refs(pinned) == []
    tagged = "steps:\n  - uses: actions/checkout@v4\n"
    assert mutable_action_refs(tagged) == [("actions/checkout", "v4")]


def test_actual_ci_workflow_has_no_mutable_action_refs():
    path = Path(".github/workflows/ci.yml")
    if not path.exists():
        print(f"FAIL CLV: workflow not found: {path}", file=sys.stderr)
        raise AssertionError("actual CI workflow must be present")
    bad = mutable_action_refs(path.read_text(encoding="utf-8"))
    assert not bad, f"mutable action references: {bad}"


if __name__ == "__main__":
    test_policy_accepts_pinned_refs_and_rejects_tags()
    test_actual_ci_workflow_has_no_mutable_action_refs()
    print("PASS CLV: workflow action pin policy (2/2 tests)")
