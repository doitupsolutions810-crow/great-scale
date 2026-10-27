# Descent CLVIII — Test reachability must be complete, not merely plausible

## Finding

The canonical CI workflow invokes `npm run all`, but the aggregate is a manually maintained shell string. A test can exist in the repository and never execute if its author forgets to add it to that string. Conversely, a stale command can name a file that no longer exists and stop the aggregate before the intended verification is complete. A reachability test that checks only a few required filenames does not prove the manifest is complete.

This is a coverage-of-the-verifier problem: CI may correctly execute its configured command while that command silently omits a newly added regression test.

## Formal contract

Let (T={t_1,ldots,t_n}) be all top-level Python test modules named `test_*.py), and let (R(C)) be the Python files referenced by the canonical aggregate command (C).

The required manifest invariant is:

[
T subseteq R(C)
quadlandquad
R(C) subseteq operatorname{ExistingFiles}
]

If every discovered test is intended to be part of the canonical suite, then the stronger invariant is:

[
T=R(C)
]

The first inclusion prevents silently omitted tests; the second prevents dangling command targets. This check addresses Python test modules referenced by `npm run all`; it does not prove that the tests' assertions are correct, that every test is scientifically adequate, or that hosted CI actually ran.

## Integrated regression

Added `test_great_scale_clviii_test_manifest_completeness.py`. It checks the repository's actual aggregate command, detects a synthetic omitted test, and detects a synthetic missing command target. It is wired into `npm run all` so future changes to the manifest are checked by the same canonical command.

## Verification boundary

The test and documentation were added to the PR branch. The repository's full `npm run all` has not been executed in a clean checkout here. An isolated model check, if separately reported, is not equivalent to a clean checkout or hosted Actions run. The current candidate still needs an actual GitHub Actions run with a completed successful result bound to its exact SHA.

## Great Scale interpretation

Verification has two levels: the tests check the system, and the manifest audit checks whether the intended tests are reachable. A green execution result is incomplete if the verifier has silently excluded part of its own specification. This is analogous to a proof whose lemmas are valid but whose dependency graph omits a required lemma.


## Descent CLXII — Reachable test files are not necessarily executed tests

The CLVIII manifest invariant establishes that test modules are referenced by the aggregate command and exist on disk. But the canonical command invokes Python modules directly (\`python3 test_*.py\`), not through pytest. Python does not automatically discover and execute functions named \`test_*\` when a file is run as a script. If a new module defines an assertion-bearing \`test_regression()\` but never calls it from its \`if __name__ == "__main__":\` entrypoint, the command can exit zero while the intended test never executes.

Let T be the test functions defined in a module and I the functions invoked by its direct-script entrypoint. File-level reachability does not prove:

\[
T \subseteq I
\]

Extended \`test_great_scale_clviii_test_manifest_completeness.py\` with an AST-based check that validates direct-runner invocation, detects a synthetic uninvoked test, and accepts a test called from the \`__main__\` guard. The regression remains included through the existing \`npm run all\` entry.

This is a structural check, not proof that assertions are non-vacuous, that all branches execute, or that hosted CI ran the exact candidate. The full aggregate and hosted Actions still need to pass against the same reviewed revision.

**Great Scale interpretation:** a test file in the manifest is analogous to a theorem written in a book; existence is not proof that it was used. Verification needs a traceable path from specification to invocation to observed result, bound to one revision.


## Descent CLXIII — CI must invoke the aggregate, not merely define it

The next boundary is between the package's canonical aggregate and the workflow that actually runs in CI. A test can be present in the manifest and npm run all yet remain absent from CI if the workflow calls only npm test plus a hand-picked subset. Therefore, the required reachability chain is:

\[
\text{Test module} \rightarrow \text{npm run all} \rightarrow \text{CI workflow} \rightarrow \text{successful run on candidate}
\]

A manifest audit that stops at package.json does not prove the workflow invokes the aggregate. Added test_ci_invokes_the_canonical_aggregate() to require .github/workflows/ci.yml to contain npm run all and reject a workflow that substitutes the narrower npm test command. This is a source-level wiring guard, not evidence that a hosted workflow actually triggered or passed.

The complete acceptance condition remains:

\[
\operatorname{AcceptCI}(R)=M\land R_t\land W\land(\operatorname{RunHead}=R)\land(\operatorname{Conclusion}=\text{success})
\]

where M is manifest completeness, R_t is test-function reachability, and W is workflow-to-aggregate wiring. Hosted execution and exact-candidate provenance remain independently required.
