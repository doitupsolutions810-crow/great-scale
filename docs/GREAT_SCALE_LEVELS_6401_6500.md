# Great Scale — Levels 6401–6500: end-to-end verification closure

**Status:** research/design note integrated on the PR #89 research branch. The reference harness described below is not the repository's official test suite. Hosted CI is still unverified; this note does not authorize a merge, deployment, or runner privilege expansion.

## Descent finding

The assurance boundary is larger than the proof kernel. A claim can be logically valid relative to its premises, and the kernel can be bounded, while the system still lacks trustworthy evidence that the exact candidate was executed and tested.

A workflow definition is not an execution. A failed job with no runner identity, no executed steps, and no logs is not evidence that the code assertions failed; equally, it is not a pass. The correct result is **execution unverified**.

This is observed on PR #89 (branch research/kernel-hardening-4401-4500, head SHA e35ad205cba2ec3953a37b6c6134083561aee050): the latest observed job completed as failure with no step summary. A retry was requested through the GitHub connector; the retried job also returned failure with no steps. These observations do not identify the root cause. A billing/authorization lock is one documented possible cause, not confirmed by the run metadata.

## Formal contract

Let C be the candidate commit, R an execution record, E its evidence bundle, and G_i the required promotion gates.

\[
\operatorname{Promote}(C)
\iff
\left(\bigwedge_i G_i(C,E)\right)
\land \operatorname{ObservedExecution}(R)
\land \operatorname{SHA}(R)=\operatorname{SHA}(C)
\land \operatorname{EvidenceCurrent}(E).
\]

A necessary identity condition is:

\[
\operatorname{SHA}_{candidate}
=
\operatorname{SHA}_{workflow}
=
\operatorname{SHA}_{receipt}
=
\operatorname{SHA}_{artifact}.
\]

This equality is necessary but not sufficient. The source of the run and artifact must be independently observable; a self-reported field such as "source: github-actions-api" does not authenticate the source. The verifier must also check issuer authority, repository, workflow identity, run attempt, executed step outcomes, freshness/revocation, and the current candidate at the moment of promotion.

## Evidence state machine

Use distinct states instead of one overloaded Boolean:

- **REFERENCE_TESTED:** bounded reference-model or local harness cases ran.
- **EXECUTION_UNVERIFIED:** no trustworthy record proves the intended test steps ran.
- **EXECUTED_FAILED:** authentic evidence shows one or more required assertions or commands failed.
- **EXECUTED_PASSED:** all required commands ran and returned success on the exact candidate SHA.
- **CI_VERIFIED:** execution passed, evidence is retrievable and current, identity matches, no required steps were skipped, and the promotion gate independently accepts the evidence.
- **STALE_OR_REVOKED:** evidence no longer applies or has been revoked; promotion is blocked.

No-step runner failures map to EXECUTION_UNVERIFIED, not EXECUTED_FAILED and not CI_VERIFIED.

## Operational mitigation

1. Inspect GitHub Actions and Billing & Licensing diagnostics to establish the actual hosted-runner failure reason. Do not infer a billing lock solely from runner_id: 0.
2. If hosted execution cannot be restored, provision a dedicated ephemeral runner scoped to doitupsolutions810-crow/great-scale, and confirm its registered labels and online status before changing workflow labels.
3. Do not route untrusted pull-request code to the current generic swarm runner without hardening: its documented compose configuration mounts /var/run/docker.sock, which is excessive privilege for a PR test worker. Use an isolated, least-privilege runner with no production secrets or Docker socket, read-only repository permissions, and a strict timeout.
4. Run the canonical script bash scripts/verify-local.sh, which executes npm test and python3 test_descent.py. Preserve the receipt, logs, step summaries, runner identity, workflow run/attempt, repository, and exact SHA.
5. Before promotion, re-fetch the PR head and confirm it still equals the tested SHA. A newer commit invalidates the old test receipt for the new candidate.
6. Keep PR #89 draft and unmerged until actual test execution, retrievable logs, current-SHA binding, and base-branch reconciliation are verified.
7. Treat Vercel deployment separately: the PR discussion reports the free-tier deployment limit (api-deployments-free-per-day). A ready preview is not proof that the Node/Python test suites ran; deployment-rate limits are not a substitute for test results.

## Bounded reference harness

An independent JavaScript harness executed in this session reported **35/35 checks passed** after correcting an overly strict finite-iteration convergence assertion. It covered:
- contraction bounds and invalid parameter rejection;
- 100,001 normalized heat inputs and invalid-domain rejection;
- circular residual invariance over 10,001 sample points;
- involution behavior over 36,001 sample points;
- a cubic counterexample to unjustified three-point polynomial inference;
- toy freshness, version mismatch, expiry, revocation, dependency-cycle, SHA-mismatch, and provenance-label checks.

These are bounded tests of the harness logic, not cryptographic verification and not execution of the committed repository suites. The official npm test, python3 test_descent.py, and npm run all have not been verified as passing in this session.

## Success criteria

Promotion remains blocked until all are true:

1. A real runner identity and executed step records are present.
2. Both JavaScript and Python suites complete with exit code 0.
3. Logs and receipt are retrievable and bind to the exact candidate SHA and run attempt.
4. No required test step was skipped.
5. Evidence issuer, scope, freshness, and revocation are checked by a trusted verifier rather than accepted from self-asserted fields.
6. The PR head still matches the tested SHA, and the branch/base divergence has been reconciled.
7. The runner is isolated and least-privileged for untrusted PR code.
8. The promotion decision is auditable and fails closed on missing, stale, contradictory, or unbound evidence.

## Great Scale candidate finding

**Verification is an end-to-end property of a claim, its premises, its model scope, the execution environment, and the evidence chain—not merely a property of a function or a green-looking status label.**

The operational corollary is precise: a system cannot certify a computation it cannot show was executed, and it cannot transfer a test result to a different commit without a new justified binding.

This is a software assurance result, not a new physical law or empirical evidence for a quantum-geometry hypothesis.
