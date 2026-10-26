# Descent CLXII — Reachable test files are not necessarily executed tests

## Finding

The CLVIII manifest invariant establishes that test modules are referenced by the aggregate command and exist on disk. But the canonical command invokes Python modules directly (\`python3 test_*.py\`), not through pytest. Python does not automatically discover and execute functions named \`test_*\` when a file is run as a script. If a new module defines an assertion-bearing \`test_regression()\` but never calls it from its \`if __name__ == "__main__":\` entrypoint, the command can exit zero while the intended test never executes.

Thus file reachability is necessary but insufficient.

## Formal contract

Let T be the test functions defined in a module, and I the test functions invoked by its direct-script entrypoint. File-level reachability proves only that the interpreter opened the module. It does not prove:

\[
T \subseteq I
\]

For the repository's current direct-Python execution model, the auditable contract is that every top-level \`test_*\` function is called from the module's \`__main__\` guard. This is a conservative structural check, not a general proof of assertion quality or runtime branch coverage.

## Integration

Extended \`test_great_scale_clviii_test_manifest_completeness.py\` with an AST-based check that:
- checks current test functions are invoked by the direct-script runner;
- detects a synthetic test function that would otherwise silently never execute;
- accepts a test function called from a \`__main__\` guard;
- retains the existing missing-target and omitted-module checks.

The regression is included in \`npm run all\` through the existing CLVIII module entry.

## Verification boundary

The new regression should be executed in a clean checkout and through the hosted Actions workflow. An AST check proves structural invocation only; it cannot prove that assertions are non-vacuous, that helper functions exercise the intended behavior, or that the test ran successfully on the exact merge candidate.

## Great Scale interpretation

A test file in the manifest is analogous to a theorem written in a book: existence is not proof that it was used. Verification requires a traceable path from specification to invocation to observed result, all bound to the same revision.
