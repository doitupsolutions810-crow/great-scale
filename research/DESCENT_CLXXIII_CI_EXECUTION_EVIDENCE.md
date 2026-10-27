# Great Scale — Descent CLXXIII: CI execution evidence is three-valued

## Finding

A workflow run that reports `conclusion=failure` is not necessarily evidence that the repository's tests failed. For the current Great Scale candidate, Actions run [40426050653](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40426050653) reports `runner_id=0` and zero executed steps. That is a runner-startup failure: the test outcome is unknown, not pass and not test-failure.

This distinction matters because treating infrastructure failure as a code failure misdirects remediation, while treating a workflow-level success from a non-executed job as test success falsely certifies the candidate.

## Formal model

Let:
- (R) mean a runner was actually assigned;
- (S) mean at least one relevant test step executed;
- (C) be the workflow conclusion.

Classify evidence as:

```text
UNKNOWN, if not R or not S
PASS,    if R and S and C = success
FAIL,    if R and S and C = failure
UNKNOWN, otherwise
```

For acceptance, require more than a label:

```text
AcceptCI(revision) =
  RunnerAssigned
  AND RelevantStepsExecuted
  AND ConclusionSuccess
  AND RunHead == revision
```

A failure to start is an operational blocker, not evidence for or against the code's correctness. Retry only after diagnosing the runner/account/workflow condition; do not weaken the tests to make the status green.

## Integration

- Added `test_great_scale_clxxiii_ci_execution_evidence.py`, covering runner-not-started, executed success, executed failure, and indeterminate states.
- Wired the test into `npm run all` in `package.json`.
- The source of the latest hosted observation is run [40426050653](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40426050653), with zero steps and `runner_id=0`.

## Verification limits

The test module and full aggregate have not been executed in a clean checkout in this step. The GitHub Actions runner startup failure prevents using that run as test evidence. The test and package changes are committed to the research branch, but the new commit has not yet been proven by a successful hosted run.

## Great Scale synthesis

```text
Manifest completeness != execution reachability
Execution reachability != actual execution
Workflow conclusion != test evidence without execution
Observed test success != acceptance unless bound to the exact reviewed revision
```

The assurance system must represent uncertainty explicitly. Three-valued evidence (PASS / FAIL / UNKNOWN) is safer than forcing every unavailable observation into a binary result.
