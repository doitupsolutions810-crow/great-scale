#!/usr/bin/env python3
"""CLIX: fail closed when aggregate shell syntax makes tests conditionally unreachable."""
import json
from pathlib import Path
import re
import tempfile


PYTHON_TEST = re.compile(r"python3\s+(test_[A-Za-z0-9_]+\.py)")


def audit_suite(root: Path, all_command: str):
    """Audit a deliberately small, fail-closed grammar for the canonical suite."""
    command_targets = []
    unsafe_segments = []
    for raw_segment in all_command.split("&&"):
        segment = raw_segment.strip()
        if segment == "npm test":
            continue
        match = PYTHON_TEST.fullmatch(segment)
        if match:
            command_targets.append(match.group(1))
        else:
            unsafe_segments.append(segment)

    missing_targets = sorted(path for path in command_targets if not (root / path).is_file())
    referenced = set(command_targets)
    discovered_tests = {path.name for path in root.glob("test_*.py") if path.is_file()}
    omitted_tests = sorted(discovered_tests - referenced)
    return missing_targets, omitted_tests, unsafe_segments


def test_current_aggregate_uses_only_supported_unconditional_commands():
    root = Path(__file__).resolve().parent
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    missing, omitted, unsafe = audit_suite(root, package["scripts"]["all"])
    assert not unsafe, f"Unsupported or conditional shell segments: {unsafe}"
    assert not missing, f"npm run all references missing Python files: {missing}"
    assert not omitted, f"Python tests omitted from npm run all: {omitted}"


def test_audit_rejects_test_hidden_behind_success_fallback():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "test_alpha.py").write_text("# present\n", encoding="utf-8")
        missing, omitted, unsafe = audit_suite(
            root, "npm test && python3 test_alpha.py || true"
        )
        assert missing == []
        assert omitted == ["test_alpha.py"]
        assert unsafe == ["python3 test_alpha.py || true"]


def test_audit_rejects_unrecognized_short_circuit_segment():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "test_alpha.py").write_text("# present\n", encoding="utf-8")
        missing, omitted, unsafe = audit_suite(
            root, "npm test && false && python3 test_alpha.py"
        )
        assert missing == []
        assert omitted == []
        assert unsafe == ["false"]


def test_audit_still_detects_omitted_and_missing_files():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "test_alpha.py").write_text("# included\n", encoding="utf-8")
        (root / "test_beta.py").write_text("# omitted\n", encoding="utf-8")
        missing, omitted, unsafe = audit_suite(
            root, "npm test && python3 test_alpha.py && python3 test_missing.py"
        )
        assert missing == ["test_missing.py"]
        assert omitted == ["test_beta.py"]
        assert unsafe == []


if __name__ == "__main__":
    tests = [
        test_current_aggregate_uses_only_supported_unconditional_commands,
        test_audit_rejects_test_hidden_behind_success_fallback,
        test_audit_rejects_unrecognized_short_circuit_segment,
        test_audit_still_detects_omitted_and_missing_files,
    ]
    for test in tests:
        test()
    print(f"PASS CLIX fail-closed shell manifest audit ({len(tests)}/{len(tests)} tests)")
