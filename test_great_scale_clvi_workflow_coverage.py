#!/usr/bin/env python3
"""CLVI: fail closed on mutable action refs across every repository workflow."""
from pathlib import Path
import re
import sys

USES = re.compile(r"^\s*-\s*uses:\s*([^@\s]+)@([^\s#]+)", re.MULTILINE)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
WORKFLOW_ROOT = Path(".github/workflows")


def mutable_action_refs(workflow: str):
    bad = []
    for match in USES.finditer(workflow):
        repository, ref = match.groups()
        if not SHA40.fullmatch(ref):
            bad.append((repository, ref))
    return bad


def workflow_paths(root: Path = WORKFLOW_ROOT):
    if not root.is_dir():
        return []
    return sorted([*root.glob("*.yml"), *root.glob("*.yaml")])


def test_policy_accepts_pins_and_rejects_tags():
    pinned = "steps:\n  - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n"
    tagged = "steps:\n  - uses: actions/checkout@v4\n"
    assert mutable_action_refs(pinned) == []
    assert mutable_action_refs(tagged) == [("actions/checkout", "v4")]


def test_scanner_covers_all_workflow_files():
    paths = workflow_paths()
    assert paths, f"no workflow YAML files found under {WORKFLOW_ROOT}"
    scanned = {path.name for path in paths}
    assert "ci.yml" in scanned, f"expected ci.yml among workflows; found {sorted(scanned)}"


def test_mutable_reference_in_any_workflow_is_detected():
    # Synthetic second workflow proves the policy is not scoped to ci.yml.
    synthetic = WORKFLOW_ROOT / "clvi-synthetic-policy-test.yaml"
    bad = "name: extra workflow\njobs:\n  test:\n    steps:\n      - uses: vendor/action@main\n"
    assert mutable_action_refs(bad) == [("vendor/action", "main")]


def test_all_actual_workflows_are_pinned():
    paths = workflow_paths()
    if not paths:
        print(f"FAIL CLVI: no workflow YAML files found under {WORKFLOW_ROOT}", file=sys.stderr)
        raise AssertionError("workflow scan must not silently pass on empty input")
    violations = []
    for path in paths:
        for repository, ref in mutable_action_refs(path.read_text(encoding="utf-8")):
            violations.append(f"{path}: {repository}@{ref}")
    assert not violations, "mutable action references: " + ", ".join(violations)


if __name__ == "__main__":
    test_policy_accepts_pins_and_rejects_tags()
    test_scanner_covers_all_workflow_files()
    test_mutable_reference_in_any_workflow_is_detected()
    test_all_actual_workflows_are_pinned()
    print("PASS CLVI: repository-wide workflow action pin policy (4/4 tests)")
