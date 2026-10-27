# Descent CLXXXVII — isolated CI still fails before runner steps

Date: 2026-10-26 (GitHub event timestamps are 2026-10-27 UTC)

## Change made

Added a focused GitHub Actions workflow to control-plane PR #33:
`.github/workflows/evidence-contract-tests.yml`

Commit: `1b2ad196dc6dfd6c6b23083fed5d8238700997da`

The workflow is deliberately independent of the full build/security pipeline. It requests Node.js 20, syntax-checks the evidence consumer, procurement producer, namespace policy and tests, then runs:

`node --test test/evidence-console.test.mjs test/gate-namespaces.test.mjs`

It has read-only repository permissions and no secrets. Its goal is to make trust-boundary regression results independently observable.

## Exact-head result

The new workflow did trigger on PR #33's exact head SHA `1b2ad196dc6dfd6c6b23083fed5d8238700997da`:
- Run: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40441231142
- Run conclusion: failure.
- Job started and completed within roughly three seconds.
- GitHub job metadata reports `steps: []`, `runner_id: 0`, and no runner name.
- Downloading job logs returns `BlobNotFound`.
- The existing Plane CI run at the same SHA, `40441231174`, shows the same zero-step failure pattern; its dependent Docker job is skipped.

This is not evidence that Node tests failed. No test step is shown as executed. The available evidence points to a pre-runner/workflow execution failure, but its exact cause is not exposed by the available GitHub metadata.

## Verification matrix

| Check | Result |
|---|---|
| Workflow file committed and re-fetched | Confirmed |
| Workflow triggered for exact PR head | Confirmed |
| Runner started / steps visible | No |
| Syntax checks executed | Unverified |
| Node regression tests executed | Unverified |
| Full npm test / platform test | Unverified |
| Production producer and deployed key binding | Unverified |

## Next mitigation

1. Preserve the focused workflow as the isolated test path.
2. Diagnose repository/account Actions runner availability and workflow execution policy in GitHub settings; this cannot be repaired from source code if GitHub rejects the job before runner allocation.
3. Once a runner executes, require visible syntax-check and Node test steps; capture logs and exact SHA.
4. Keep production authorization HOLD until those checks and live trust binding pass.

This finding is evidence of a CI observability/execution blocker, not a test pass, not a test failure, and not proof of production readiness.
