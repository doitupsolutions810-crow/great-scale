#!/usr/bin/env python3
"""CLVIII/CLXII/CLXV: audit test reachability and executable Python test entrypoints."""
import ast
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


def tests_not_invoked_by_direct_runner(path: Path):
    """Find test_* functions not called directly or through an executed registry."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    defined = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }

    def referenced_tests(node):
        return {
            child.id for child in ast.walk(node)
            if isinstance(child, ast.Name) and child.id in defined
        }

    def assigned_names(node):
        if isinstance(node, ast.Name):
            return {node.id}
        if isinstance(node, (ast.Tuple, ast.List)):
            return {
                child.id for child in ast.walk(node)
                if isinstance(child, ast.Name)
            }
        return set()

    def inspect_block(statements, registry):
        invoked = set()
        known_registries = dict(registry)
        for statement in statements:
            invoked.update(
                child.func.id for child in ast.walk(statement)
                if isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id in defined
            )

            if isinstance(statement, ast.Assign):
                value = statement.value
                if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
                    tests = referenced_tests(value)
                    for target in statement.targets:
                        for name in assigned_names(target):
                            known_registries[name] = tests
            elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
                value = statement.value
                if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
                    tests = referenced_tests(value)
                    for name in assigned_names(statement.target):
                        known_registries[name] = tests

            if isinstance(statement, ast.For):
                loop_targets = assigned_names(statement.target)
                loop_calls = {
                    child.func.id for child in ast.walk(statement)
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                }
                if loop_targets & loop_calls:
                    if isinstance(statement.iter, ast.Name):
                        invoked.update(known_registries.get(statement.iter.id, set()))
                    elif isinstance(statement.iter, (ast.List, ast.Tuple, ast.Set)):
                        invoked.update(referenced_tests(statement.iter))
                invoked.update(inspect_block(statement.body, known_registries))
                invoked.update(inspect_block(statement.orelse, known_registries))
            elif isinstance(statement, ast.If):
                invoked.update(inspect_block(statement.body, known_registries))
                invoked.update(inspect_block(statement.orelse, known_registries))
        return invoked

    invoked = set()
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        is_main_guard = (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value == "__main__"
        )
        if is_main_guard:
            invoked.update(inspect_block(node.body, {}))
    return sorted(defined - invoked)


def test_current_aggregate_references_existing_python_files():
    root = Path(__file__).resolve().parent
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    missing, omitted = audit_suite(root, package["scripts"]["all"])
    assert not missing, f"npm run all references missing Python files: {missing}"
    assert not omitted, f"Python tests omitted from npm run all: {omitted}"


def test_current_python_test_functions_are_invoked():
    root = Path(__file__).resolve().parent
    bad = {
        path.name: tests_not_invoked_by_direct_runner(path)
        for path in root.glob("test_*.py")
        if path.is_file() and tests_not_invoked_by_direct_runner(path)
    }
    assert not bad, f"Python test functions not invoked by direct runner: {bad}"


def test_ci_invokes_the_canonical_aggregate():
    root = Path(__file__).resolve().parent
    workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "npm run all" in workflow, "CI must invoke the canonical npm run all aggregate"
    assert "npm test" not in workflow, "CI must not bypass the aggregate with a narrower test command"


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


def test_audit_detects_test_functions_that_python_would_not_run():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_silent.py"
        path.write_text("def test_regression():\n    assert False\n", encoding="utf-8")
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_accepts_test_functions_called_by_main_guard():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_active.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n    test_regression()\n',
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == []


def test_audit_accepts_functions_dispatched_from_a_main_guard_registry():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_registry.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    tests = [test_regression]\n"
            "    for test in tests:\n        test()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == []


def test_audit_rejects_an_unexecuted_test_registry():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_unexecuted_registry.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    tests = [test_regression]\n"
            "    print(tests)\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_a_bare_reference_to_test_function():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_reference_only.py"
        path.write_text(
            "def test_regression():\n    assert False\n\n"
            'if __name__ == "__main__":\n    print(test_regression)\n',
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


if __name__ == "__main__":
    tests = [
        test_current_aggregate_references_existing_python_files,
        test_current_python_test_functions_are_invoked,
        test_ci_invokes_the_canonical_aggregate,
        test_audit_detects_an_omitted_test_module,
        test_audit_detects_a_dangling_command_target,
        test_audit_detects_test_functions_that_python_would_not_run,
        test_audit_accepts_test_functions_called_by_main_guard,
        test_audit_accepts_functions_dispatched_from_a_main_guard_registry,
        test_audit_rejects_an_unexecuted_test_registry,
        test_audit_rejects_a_bare_reference_to_test_function,
    ]
    for test in tests:
        test()
    print(f"PASS CI-wired manifest and executable-entrypoint audit ({len(tests)}/{len(tests)} tests)")
