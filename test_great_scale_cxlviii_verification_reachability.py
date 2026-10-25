#!/usr/bin/env python3
"""CXLVIII: ensure canonical CI can reach the required regression suite."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_ci_trigger_reaches_stacked_pull_requests():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    # An unfiltered pull_request trigger covers PRs targeting non-main branches.
    assert "  pull_request:\n" in workflow
    assert "  pull_request:\n    branches:" not in workflow
    assert "      - run: npm run all" in workflow


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
    test_ci_trigger_reaches_stacked_pull_requests()
    test_aggregate_suite_contains_required_regressions()
    print("PASS CXLVIII: workflow trigger and canonical test reachability contract")
