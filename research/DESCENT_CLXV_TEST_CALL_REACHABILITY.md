# Descent CLXV — Test references are not test calls

## Finding

The CLXII entrypoint audit attempted to infer whether a top-level `test_*` function was invoked under the Python `__main__` guard. Its original AST walk treated any `ast.Name` occurrence matching a test function as invocation. That is weaker than the property being claimed.

A minimal counterexample is:

```python
def test_regression():
    assert False

if __name__ == "__main__":
    print(test_regression)
```

This references the function object but never calls it. Counting names rather than call expressions can therefore report a regression as reachable even though its assertion is not executed.

## Correction and next seam

The audit rejects a bare reference and recognizes two bounded executable forms beneath the `__main__` guard: a direct call to a test function, or a literal test registry assigned to a name and then dispatched by a loop that calls its loop variable. The latter covers the repository’s existing pattern:

```python
tests = [test_one, test_two]
for test in tests:
    test()
```

A full `npm run all` on the next PR candidate initially exposed a false positive: the direct-call-only audit marked registry-dispatched functions as uninvoked. The auditor now recognizes the registry only when the loop actually calls its target. Separate fixtures require an unexecuted registry and a bare function reference to remain rejected.

The key distinction is:

\[
\operatorname{Referenced}(f) \not\Rightarrow \operatorname{Called}(f).
\]

Recognizing a registry dispatch fixes the false positive but does not turn syntax into runtime evidence. A call inside a branch that never executes, an exception before the loop, or a test that is never discovered by the intended runner can still defeat a simple AST heuristic.

## Great Scale mapping

For a test function \(f\), define \(D(f)\) as its definition, \(N(f)\) as a name reference, \(C(f)\) as a direct or bounded registry-dispatch call beneath the accepted entrypoint, and \(X(f)\) as observed runtime execution. The original audit used \(N(f)\) as a proxy for \(C(f)\); the direct-call revision then missed the repository’s registry-dispatch form.

\[
D(f) \land C(f) \not\Rightarrow X(f).
\]

The current audit checks known static reachability forms. It remains a guard against specific false positives, not a complete Python control-flow analysis or coverage proof. A test runner that reports collected and executed tests remains stronger evidence.

## Verification status

- The original bare-reference fixture still requires `test_regression` to be reported as uninvoked.
- The new registry fixtures cover both an actually dispatched test list and a list that is only printed, not executed.
- `python3 test_great_scale_clviii_test_manifest_completeness.py` — **10/10 passed**, exit code **0**.
- `npm run all` — **passed**, exit code **0**, after the direct-dispatch false positive was corrected.
- `git diff --check` — exit code **0**.
- These results are local. They do not prove a hosted Actions run or runtime coverage beyond the commands actually executed.
