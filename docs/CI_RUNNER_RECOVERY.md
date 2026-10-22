# CI Runner Recovery — Great Scale

## Observed condition

Recent GitHub Actions jobs for this branch complete as failures within about two seconds. The job metadata reports `runner_id: 0`, empty runner name, no executed steps, and no log URL. Retrying an earlier failed run reproduced the same no-step signature. Therefore the full repository test suite has not been shown to execute in hosted CI.

## Cross-repository evidence

The accessible `doitupsolutions810-crow/swarm-vm-runner` README explicitly documents that hosted Ubuntu pools currently fail with `runner_id 0` and recommends the labels `[self-hosted, linux, control12]`. Its compose configuration shows an **ephemeral, repository-scoped** Actions runner whose default target is `doitupsolutions810-crow/control12-workspace`, not `great-scale`. It requires a repository runner registration token and has a Docker socket mount in its current generic runner service.

The `doitupsolutions810-crow/capability-authority` repository's `docs/CI.md` separately documents an account-level GitHub billing lock as one cause of immediate hosted-runner failure and provides a local CI route. The present Great Scale job metadata does not expose the billing error text, so a billing lock is a plausible cause, not a confirmed diagnosis.

## Safe recovery order

1. In GitHub account/repository settings, inspect Actions and Billing & Licensing diagnostics. If GitHub reports a billing/authorization lock, resolve it through GitHub's official settings/support path.
2. Alternatively, register a **dedicated ephemeral runner for `doitupsolutions810-crow/great-scale`** and confirm it appears online before changing the workflow. The existing runner configuration targets `control12-workspace`; do not assume it can service this repository.
3. If using self-hosted execution, use a least-privilege runner with no Docker socket or production credentials for pull-request tests. A self-hosted runner executes repository code; do not route untrusted fork PRs to a privileged host. Keep the job read-only, time-bounded, ephemeral, and isolated.
4. Only after the runner is confirmed online, change the CI job labels to the runner's registered labels and dispatch a run.
5. Verify that the check-run contains real checkout/setup/test steps and logs. Require both `npm test` and `python3 test_descent.py` to pass on the exact PR head SHA.
6. Keep PR #89 draft and unmerged until these checks succeed. A Vercel preview/deployment success is not a substitute for test execution.

## Promotion gate

`CI_VERIFIED` requires all of:
- observed runner identity and nonempty executed-step records;
- logs tied to the exact commit SHA;
- JavaScript and Python suites completed with exit code 0;
- no skipped required test steps;
- read-only permissions and timeout controls;
- current code still matches the tested commit.

Until then the state is `REFERENCE_TESTED / HOSTED_CI_UNVERIFIED`. Do not infer a code failure from a no-runner failure, and do not infer a code pass from a workflow definition.

## Great Scale candidate principle

**A verification system cannot certify a computation that never reached its execution environment.** The runner is part of the evidence chain, not incidental infrastructure.
