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
    """Fail closed unless top-level sync tests are provably reachable through a supported runner."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    defined = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }
    # A bare async call only creates a coroutine. This synchronous auditor does not
    # certify async tests until it has an explicit await/scheduler model.
    synchronous_defined = {
        node.name for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
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

    def referenced_tests(node):
        # Accept only bare test-function references in literal registries. Do not
        # treat a test name captured by lambda/comp/call expressions as dispatch.
        if isinstance(node, ast.Name):
            return {node.id} if node.id in synchronous_defined else set()
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            result = set()
            for item in node.elts:
                result.update(referenced_tests(item))
            return result
        return set()

    def literal_truth(node):
        """Return (known, truth) for a deliberately small side-effect-free subset."""
        if isinstance(node, ast.Constant):
            return True, bool(node.value)
        if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            # Only empty literals are accepted: non-empty values may contain effects.
            if not node.elts if isinstance(node, (ast.List, ast.Tuple, ast.Set)) else not node.keys:
                return True, False
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            known, value = literal_truth(node.operand)
            return (True, not value) if known else (False, False)
        if isinstance(node, ast.BoolOp):
            values = [literal_truth(value) for value in node.values]
            if not all(known for known, _ in values):
                return False, False
            truths = [value for _, value in values]
            if isinstance(node.op, ast.And):
                return True, all(truths)
            if isinstance(node.op, ast.Or):
                return True, any(truths)
        return False, False

    def definitely_empty_iterable(node):
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)) and len(node.elts) == 0:
            return True
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "range" and not node.keywords
                and 1 <= len(node.args) <= 3
                and all(isinstance(arg, ast.Constant) and type(arg.value) is int
                        for arg in node.args)):
            values = [arg.value for arg in node.args]
            if len(values) == 1:
                start, stop, step = 0, values[0], 1
            elif len(values) == 2:
                start, stop, step = values[0], values[1], 1
            else:
                start, stop, step = values
            if step == 0:
                return True  # range() raises before its body can execute
            return (step > 0 and start >= stop) or (step < 0 and start <= stop)
        return False

    def calls_loop_target_in_reachable_block(statements, target_names):
        """Find loop-variable calls without descending into nested scopes/dead paths."""
        class ReachableCallVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found = False

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id in target_names:
                    self.found = True
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                return

            visit_AsyncFunctionDef = visit_FunctionDef
            visit_Lambda = visit_FunctionDef
            visit_ClassDef = visit_FunctionDef

            def visit_If(self, node):
                self.visit(node.test)
                known, truth = literal_truth(node.test)
                selected = node.body if known and truth else node.orelse if known else node.body + node.orelse
                for child in selected:
                    self.visit(child)

            def visit_While(self, node):
                self.visit(node.test)
                known, truth = literal_truth(node.test)
                selected = node.body if known and truth else node.orelse if known else node.body + node.orelse
                for child in selected:
                    self.visit(child)

            def visit_For(self, node):
                self.visit(node.iter)
                selected = node.orelse if definitely_empty_iterable(node.iter) else node.body + node.orelse
                for child in selected:
                    self.visit(child)

            visit_AsyncFor = visit_For

            def visit_Try(self, node):
                # Exception reachability is not statically proven by this auditor.
                return

            visit_TryStar = visit_Try

            def visit_With(self, node):
                # Context-manager entry can fail; do not certify calls under it.
                return

            visit_AsyncWith = visit_With

            def visit_Match(self, node):
                # Pattern reachability is outside the supported static subset.
                return

        visitor = ReachableCallVisitor()
        for statement in statements:
            visitor.visit(statement)
        return visitor.found

    def inspect_block(statements, registry):
        invoked = set()
        known_registries = dict(registry)
        for statement in statements:
            # Only count a syntactically direct expression call. Avoid ast.walk over
            # assignments/lambdas/try/match/etc., which can contain non-executed calls.
            if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                call = statement.value
                if isinstance(call.func, ast.Name) and call.func.id in synchronous_defined:
                    invoked.add(call.func.id)

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

            if isinstance(statement, ast.If):
                known, truth = literal_truth(statement.test)
                selected = statement.body if known and truth else statement.orelse if known else statement.body + statement.orelse
                invoked.update(inspect_block(selected, known_registries))
            elif isinstance(statement, ast.For):
                if not definitely_empty_iterable(statement.iter):
                    loop_targets = assigned_names(statement.target)
                    if calls_loop_target_in_reachable_block(statement.body, loop_targets):
                        if isinstance(statement.iter, ast.Name):
                            invoked.update(known_registries.get(statement.iter.id, set()))
                        elif isinstance(statement.iter, (ast.List, ast.Tuple, ast.Set)):
                            invoked.update(referenced_tests(statement.iter))
                    invoked.update(inspect_block(statement.body, known_registries))
                invoked.update(inspect_block(statement.orelse, known_registries))
            elif isinstance(statement, ast.While):
                known, truth = literal_truth(statement.test)
                if known and not truth:
                    invoked.update(inspect_block(statement.orelse, known_registries))
                else:
                    invoked.update(inspect_block(statement.body, known_registries))
                    invoked.update(inspect_block(statement.orelse, known_registries))
            # Function/class definitions, with/try/match, and other unsupported
            # compound statements are deliberately not traversed: fail closed.

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


def test_audit_rejects_a_test_call_in_a_false_branch():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_dead_branch.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    if False:\n        test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_loop_dispatch_in_a_false_branch():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_dead_loop_branch.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    for test in [test_regression]:\n"
            "        if False:\n"
            "            test()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_loop_dispatch_inside_an_uninvoked_helper():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_nested_helper.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    for test in [test_regression]:\n"
            "        def helper():\n"
            "            test()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_test_call_in_false_while_loop():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_dead_while.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    while False:\n"
            "        test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_unawaited_async_test_invocation():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_unawaited_async.py"
        path.write_text(
            "async def test_regression():\n    assert False\n\n"
            'if __name__ == "__main__":\n'
            "    test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_loop_dispatch_inside_false_while():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_nested_dead_while.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    for test in [test_regression]:\n"
            "        while False:\n"
            "            test()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_loop_dispatch_inside_empty_nested_loop():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_empty_nested_loop.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    for test in [test_regression]:\n"
            "        for unused in []:\n"
            "            test()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_false_numeric_condition():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_numeric_false.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    if 0:\n"
            "        test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_negated_true_condition():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_negated_true.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    if not True:\n"
            "        test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_direct_call_under_empty_loop():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_direct_empty_loop.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    for unused in range(0):\n"
            "        test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_call_in_uninvoked_lambda():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_lambda.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    callback = lambda: test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_lambda_wrapped_test_in_registry():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_lambda_registry.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    tests = [lambda: test_regression()]\n"
            "    for test in tests:\n"
            "        test()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


def test_audit_rejects_call_under_unsupported_try_branch():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "test_try_branch.py"
        path.write_text(
            "def test_regression():\n    assert True\n\n"
            'if __name__ == "__main__":\n'
            "    try:\n"
            "        pass\n"
            "    except Exception:\n"
            "        test_regression()\n",
            encoding="utf-8",
        )
        assert tests_not_invoked_by_direct_runner(path) == ["test_regression"]


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
        test_audit_rejects_a_test_call_in_a_false_branch,
        test_audit_rejects_loop_dispatch_in_a_false_branch,
        test_audit_rejects_loop_dispatch_inside_an_uninvoked_helper,
        test_audit_rejects_test_call_in_false_while_loop,
        test_audit_rejects_unawaited_async_test_invocation,
        test_audit_rejects_loop_dispatch_inside_false_while,
        test_audit_rejects_loop_dispatch_inside_empty_nested_loop,
        test_audit_rejects_false_numeric_condition,
        test_audit_rejects_negated_true_condition,
        test_audit_rejects_direct_call_under_empty_loop,
        test_audit_rejects_call_in_uninvoked_lambda,
        test_audit_rejects_lambda_wrapped_test_in_registry,
        test_audit_rejects_call_under_unsupported_try_branch,
    ]
    for test in tests:
        test()
    print(f"PASS CI-wired manifest and executable-entrypoint audit ({len(tests)}/{len(tests)} tests)")
