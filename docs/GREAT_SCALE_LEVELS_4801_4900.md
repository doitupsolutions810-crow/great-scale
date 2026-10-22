# Great Scale Levels 4801–4900 — Make the verification path reproducible, then distinguish it from hosted execution

## Descent finding

The current GitHub Actions workflow already has `workflow_dispatch`, read-only `contents: read` permissions, `ubuntu-latest`, Node 20, Python 3.11, and a ten-minute timeout. Repeated runs still fail in roughly two seconds without executed steps or logs. Therefore adding more in-workflow test assertions cannot fix the observed no-runner condition.

The mitigation has two distinct targets: eliminate drift between local and hosted test commands, and preserve the execution-evidence boundary so a local pass is never mislabeled as hosted CI verification.

## Code-side changes on the draft PR branch

- The truth-table checker now requires the assumptions value to be an ordinary dense array with the standard Array prototype and only numeric own entries plus `length`. It rejects sparse arrays, custom array properties, and custom prototypes.
- The sparse-array regression was updated to accept the stricter schema rejection. During adversarial review, the first equivalent harness exposed a mismatch between the old test's expected error and the new earlier schema gate. The expectation was corrected, and the subsequent reference harness passed all 15 checks.
- Added `scripts/verify-local.sh`, a single canonical entry point that checks Node 20 and Python 3.11, runs `npm test` (including `test_truth_table_kernel.js`), then runs `python3 test_descent.py`, stopping on any failure.
- Updated `.github/workflows/ci.yml` to invoke the same canonical script and upload its receipt artifact even on test failure. This reduces local/CI command drift and preserves outcome evidence when a runner actually executes; it does not itself make a runner available.
- The receipt schema `great-scale.verification-receipt/v1` binds the commit, runtime versions, JS/Python suite states, overall exit status, UTC creation time, and GitHub run metadata. The script preserves a failing exit code after writing the receipt.

## Executed reference test

The equivalent JavaScript adversarial harness passed **15/15 checks**:
1. valid modus ponens accepted;
2. invalid entailment returns a counterexample;
3. cyclic AST rejected by depth bound;
4. aggregate AST-node cap enforced;
5. cumulative evaluation-work cap enforced;
6. inherited valuation property rejected;
7. non-Boolean assignment rejected;
8. unexpected AST keys rejected;
9. inherited AST object rejected;
10. sparse assumptions rejected;
11. oversized assumption list rejected;
12. accessor-backed claim rejected without invoking its accessor;
13. 17-variable claim rejected;
14. custom assumption-array keys rejected;
15. custom assumption-array prototype rejected.

This is a reference execution of equivalent checker logic, not execution of the committed repository's full test suite. A separate 10/10 repository-source/configuration inspection confirmed the guards and test-command wiring are present on the branch. The current equivalent-logic harness passed 15/15; it does not execute the shell script, npm suite, or Python suite.

## Hosted execution remains unresolved

The latest inspected hosted run for the preceding head still had a failed job with no step summaries or log URL. Further commits now add a receipt artifact step, but no runner execution has been observed for the updated head yet. The runner issue is external to the source-level checks. The workflow is already manually dispatchable, but the available GitHub connector does not expose a workflow-dispatch operation, and the failed run provides no usable logs to diagnose billing or authorization.

Do not claim that the local fallback is enabled or that hosted CI is fixed. To close this connection:
1. Inspect GitHub Actions/Billing diagnostics in repository/account settings.
2. If needed, register a dedicated ephemeral runner scoped to `doitupsolutions810-crow/great-scale`; do not reuse the other repository's Docker-socket runner for untrusted PR code.
3. Confirm runner identity and real step logs.
4. Run `bash scripts/verify-local.sh` on the exact PR head with Node 20 and Python 3.11.
5. Require `npm test` and `python3 test_descent.py` exit code zero on that exact SHA before promotion.

## Promotion state

- `REFERENCE_TESTED`: equivalent logic harness passes 15/15.
- `SOURCE_WIRING_INSPECTED`: canonical script, CI reference, and test entry point present on the branch.
- `LOCAL_FULL_SUITE`: not run in this environment.
- `HOSTED_CI_VERIFIED`: no.
- `PRODUCTION_APPROVED`: no.

## Great Scale candidate principle

**A robust verification system needs one canonical test contract and multiple honestly distinguished execution states.** Reproducibility comes from a shared procedure; assurance comes from evidence that the procedure actually ran in the intended environment on the intended revision.

The final unconnected connection is not another mathematical identity. It is the external execution authority: an observable runner, a fixed commit, and recorded test outcomes. Until that exists, the correct state is unresolved—not success.

This is a software-assurance and workflow-engineering finding, not empirical evidence for a physical quantum-geometry law.
