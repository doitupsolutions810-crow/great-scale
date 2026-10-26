#!/usr/bin/env python3
"""CLVIII: enforce aggregate test-manifest completeness and command validity."""
import json
from pathlib import Path
import re
import tempfile


PYTHON_COMMAND = re.compile(r"(?:^|&&)\s*python3\s+([^\s&;]+)")


def audit_suite(root: Path, all_command: str):
    """Return missing command targets and Python tests omitted from the aggregate."""
    command_targets = PYTHON_COMMAND.findall(all_command)
    missing_targets = sorted(path for path in command_targets if not (root / path).is_file())
    referenced = set(command_targets)
    discovered_tests = {path.name for path in root.glob("test_*.py") if path.is_file()}
    omitted_tests = sorted(discovered_tests - referenced)
    return missing_targets, omitted_tests


def test_current_aggregate_references_existing_python_files():
    root = Path(__file__).resolve().parent
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    missing, omitted = audit_suite(root, package["scripts"]["all"])
    assert not missing, f"npm run all references missing Python files: {missing}"
    assert not omitted, f"Python tests omitted from npm run all: {omitted}"


def test_audit_detects_an_omitted_test_module():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "test_alpha.py").write_text("# included\n", encoding="utf-8")
        (root / "test_beta.py").write_text("# accidentally omitted\n", encoding="utf-8")
        missing, omitted = audit_suite(root, "python3 test_alpha.py")
        assert missing == []
        assert omitted == ["test_beta.py"]


def test_audit_detects_a_dangling_command_target():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "test_alpha.py").write_text("# present\n", encoding="utf-8")
        missing, omitted = audit_suite(root, "python3 test_alpha.py && python3 test_missing.py")
        assert missing == ["test_missing.py"]
        assert omitted == []


if __name__ == "__main__":
    tests = [
        test_current_aggregate_references_existing_python_files,
        test_audit_detects_an_omitted_test_module,
        test_audit_detects_a_dangling_command_target,
    ]
    for test in tests:
        test()
    print(f"PASS CLVIII aggregate test-manifest completeness ({len(tests)}/{len(tests)} tests)")
