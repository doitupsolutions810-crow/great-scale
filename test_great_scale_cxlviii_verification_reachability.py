#!/usr/bin/env python3
"""CXLVIII/CLXVIII: ensure canonical CI reaches the required regression suite."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEST_STEP_NAME = "Run canonical aggregate"


def test_ci_trigger_reaches_stacked_pull_requests():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    # An unfiltered pull_request trigger covers PRs targeting non-main branches.
    assert "  pull_request:\n" in workflow
    assert "  pull_request:\n    branches:" not in workflow


def test_ci_names_and_unconditionally_runs_the_canonical_aggregate():
    lines = (ROOT / ".github" / "workflows" / "ci.yml").read_text().splitlines()
    marker = f"      - name: {TEST_STEP_NAME}"
    assert marker in lines, f"workflow must expose step {TEST_STEP_NAME!r} to the jobs API"
    start = lines.index(marker)
    step_block = []
    for line in lines[start + 1:]:
        if line.startswith("      - "):
            break
        if line.strip() and len(line) - len(line.lstrip()) < 6:
            break
        step_block.append(line)
    assert "        run: npm run all" in step_block
    assert not any(line.lstrip().startswith("if:") for line in step_block)
    assert not any(line.lstrip().startswith("continue-on-error:") for line in step_block)

    # A job-level condition could skip the whole job while GitHub reports Success.
    test_job = lines[lines.index("  test:") + 1:]
    assert not any(line.startswith("    if:") for line in test_job)


def test_aggregate_suite_contains_required_regressions():
    package = json.loads((ROOT / "package.json").read_text())
    all_command = package["scripts"]["all"]
    required = (
        "test_effect_evidence_boundary.py",
        "test_great_scale_cxlv_atomic_projection.py",
        "test_great_scale_cxlvii_quotient_seam.py",
        "test_great_scale_cxlviii_verification_reachability.py",
    )
    for path in required:
        assert path in all_command, f"{path} is not reachable from npm run all"


if __name__ == "__main__":
    tests = [
        test_ci_trigger_reaches_stacked_pull_requests,
        test_ci_names_and_unconditionally_runs_the_canonical_aggregate,
        test_aggregate_suite_contains_required_regressions,
    ]
    for test in tests:
        test()
    print(f"PASS CXLVIII/CLXVIII workflow and test-step reachability ({len(tests)}/{len(tests)} tests)")
