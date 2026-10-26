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
