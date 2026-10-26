# Descent CLXV — Test references are not test calls

## Finding

The CLXII entrypoint audit attempted to infer whether a top-level `test_*` function was invoked under the Python `__main__` guard. Its AST walk treated any `ast.Name` occurrence matching a test function as invocation. That is weaker than the property being claimed.

Counterexample:

```python
def test_regression():
    assert False

if __name__ == "__main__":
    print(test_regression)
```

This references the function object but never calls it. An audit that counts names rather than call expressions can therefore report the regression as reachable even though its assertion is not executed.

## Correction

The audit now counts a function only when the AST contains an `ast.Call` whose direct callee is that function's name, under the recognized `__main__` guard. A regression fixture exercises the bare-reference counterexample and requires the audit to flag `test_regression` as uninvoked.

The key distinction is:

[
\operatorname{Referenced}(f) \not\Rightarrow \operatorname{Called}(f)
]

## Great Scale mapping

For a test (f), define (D(f)) as a definition, (N(f)) as a name reference, (C(f)) as a syntactic call beneath the accepted entrypoint, and (X(f)) as observed runtime execution. The original audit used (N(f)) as a proxy for (C(f)). The revised audit checks (C(f)), but static syntax alone still does not prove (X(f)): calls in unreachable branches, exceptions before the call, or indirect dispatch can defeat a simple AST heuristic.

Therefore this audit is a guard against one known false positive, not a complete Python control-flow or runtime-coverage proof. The strongest evidence remains a test runner that reports executed tests and fails when expected tests are not collected.

[
D(f) \land C(f) \not\Rightarrow X(f)
]

## Verification status

- Source inspection: confirmed the previous implementation counted any matching `ast.Name` inside the main guard.
- Regression added: bare reference via `print(test_regression)` must be reported as uninvoked.
- Aggregate wiring: the existing `npm run all` command already invokes `test_great_scale_clviii_test_manifest_completeness.py`; no package-script edit was required for this correction.
- Runtime validation: a focused local mutation harness should check both the old false positive and the corrected call-detection behavior. The committed full aggregate and hosted Actions run must be verified separately; this note does not claim either passed.

## Next boundary

Replace syntactic heuristics with explicit test-runner collection and execution evidence where practical. Do not describe an AST call-site as proof that a test executed.
