# Descent CLXVII — A runner block is not a test failure

## Finding

The next seam is epistemic, not numerical: a GitHub check marked `failure` does not prove that tests failed. On four repositories under the same owner, GitHub recorded failed Actions jobs with no runner and zero executed steps, then annotated them: “The job was not started because your account is locked due to a billing issue.” Great Scale’s current CI evidence model recorded provider, commit identity, workflow, event, status, and conclusion, but omitted runner assignment, step count, and blocker annotation. Consequently, its prior classifier labeled a billing-blocked job `FAIL` even though no test executed.

The profound distinction is:

\[
\text{workflow conclusion} \neq \text{test outcome}
\]

A conclusion becomes evidence about test execution only when the designated job actually ran.

## Live observation and cross-repository connection

All four repositories currently report `actions/permissions.enabled = true` and `allowed_actions = all`; repository-level disabling is not the observed cause. Five failed job records showed blank runner names and empty step lists; a dependent LICP container job was skipped. The same billing-lock annotation appeared across all four projects:

| Repository | Exact observed run | Job evidence | Candidate relationship |
|---|---|---|---|
| [Great Scale](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40392042836) | Run 40392042836; head `9618c609…` | `build-test`; no runner; zero steps; account-lock annotation | Historical run is off-head. Pre-integration PR #128 head `041f243c…` had zero check-runs; the CLXVII commit creates a new candidate that needs its own qualifying run, so it remains `UNKNOWN` |
| [Living Intermediate Control Plane](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40406318969) | Run 40406318969; PR #27 head `3650fe36…` | `Verify, doctor, test, Trivy FS, Snyk`; no steps; account-lock annotation; dependent container job skipped | Exact current PR head; `BLOCKED` |
| [Capability Authority](https://github.com/doitupsolutions810-crow/capability-authority/actions/runs/40223320786) | Run 40223320786; integration head `7ce3dba1…` | Both `test` and `slim-probe`; no runner; zero steps; same annotation | Exact audited branch head; test evidence `BLOCKED` |
| [CycleKernal](https://github.com/doitupsolutions810-crow/CycleKernal/actions/runs/40392038552) | Run 40392038552; PR #9 head `d82f381f…` | `test`; no runner; zero steps; same annotation | Exact current PR head; `BLOCKED` |

This is one common account-level interruption crossing four integrations—not four code defects. The Vercel failures are separate deployment/build-rate-limit statuses and do not explain why GitHub Actions never assigned a runner.

## Mitigation implemented in Great Scale

The canonical CI evidence model now carries the designated `job_name`, `runner_name`, `step_count`, and `blocker_reason`, alongside repository, run, commit, workflow, event, status, and conclusion identity. Its decision set is:

\[
D_{CI}\in\{\texttt{PASS},\texttt{FAIL},\texttt{BLOCKED},\texttt{UNKNOWN}\}.
\]

For an exact current pull-request candidate and designated test job:

\[
D_{CI}=
\begin{cases}
\texttt{BLOCKED}, & \text{explicit billing-lock annotation and zero steps},\\
\texttt{UNKNOWN}, & \text{no runner/steps and no authoritative blocker},\\
\texttt{PASS}, & \text{runner assigned, steps executed, completed success},\\
\texttt{FAIL}, & \text{runner assigned, steps executed, completed failure},\\
\texttt{UNKNOWN}, & \text{otherwise.}
\end{cases}
\]

The account lock is represented as an operational blocker, not recast as a test assertion failure. Missing execution evidence does not become a pass either. The model is intentionally fail-closed.

## Great Scale mapping

Keep the science scalar and evidence/governance state distinct. The existing scalar remains

\[
\Psi=\mathrm{CONE}+S.
\]

The decision/evidence vector expands to

\[
V=(\Psi, C, T, E, B, P, R),
\]

where:

- \(C\): candidate head/base identity and freshness are bound;
- \(T\): the intended test job has a completed conclusion;
- \(E\): runner and nonzero step execution are observed;
- \(B\): any provider-reported pre-execution blocker is captured;
- \(P\): an active server-side rule requires the intended check;
- \(R\): exact required check context and target ref.

The merge gate is

\[
\operatorname{MayMerge}=\mathbf{1}[C]\,\mathbf{1}[P]\,\mathbf{1}[D_{CI}=\texttt{PASS}].
\]

`BLOCKED`, `UNKNOWN`, `FAIL`, stale evidence, or absent enforcement all imply `MayMerge = 0`. Thus the framework preserves the lower geometric bound while separately refusing to overstate software verification.

## Test, verify, run

A baseline reproduction on the prior model classified a synthetic exact-SHA billing-blocked job as `fail`; the schema had nowhere to record that no runner or step existed. The regression now verifies all four outcomes: executed success → `PASS`; executed failure → `FAIL`; explicit zero-step account lock → `BLOCKED`; unexplained zero-step failure or unexecuted success → `UNKNOWN`. It also checks stale SHA, wrong job, incomplete status, and a green external Vercel status.
The required job identity is not inferred when it is absent; an unnamed job is also `UNKNOWN`.

- `python3 test_great_scale_clviii_three_valued_ci_evidence.py` — **8/8 passed**.
- `npm run all` — **passed**; it invokes this existing test module through the canonical aggregate and passes the manifest-completeness audit.
- No hosted GitHub job executed during this test run. Local success verifies the classifier only; it does not clear the billing lock or establish live CI.

## Operational recovery and activation criteria

GitHub’s documentation says standard hosted runners are free for public repositories, yet a locked account can block Actions/free-tier access; a failed authorization hold can cause such a lock.[1] [2] Do not upgrade or change payment information on the user’s behalf. The owner must inspect **Settings → Billing & Licensing → Payment information**. If the billing page presents an intended payment/subscription issue, the owner may resolve it directly. If no subscription, balance, or payment issue appears, GitHub directs the owner to Support to request a billing-lock review.[2]

Do **not** activate required checks yet. GitHub requires a successful status check within the previous seven days to select it, and required checks must pass on the latest commit SHA. A `workflow_dispatch` run on a PR head is not, by itself, an eligible required PR check; use a qualifying `pull_request` or `push` workflow event.[3] Current hosted logs provide no executed successful job, and previous live audit CLXVI found no active protection/rulesets.

Resume in this order:

1. Owner clears or gets GitHub to review the billing lock; do not disclose payment details to this agent.
2. Rerun or retrigger each workflow with a qualifying `pull_request`/`push` event.
3. For each exact head/base, verify a runner was assigned, at least one relevant step executed, the intended test job passed, and no billing annotation remains. For Great Scale, obtain an eligible run on the current PR #128 head—not the historical `9618c609…` run.
4. Record each exact job check context and target branch; then create active protections requiring those checks. Keep direct-push/bypass and review-count choices explicit; do not require `slim-probe` as a test.
5. Query provider policy again, verify the exact required check is active for the target ref, and use a disposable failing PR to confirm GitHub itself rejects a missing/failing check without merging it.

Until these criteria hold, server enforcement is `NOT_ENFORCED` and CI for the three exact blocked candidates is `BLOCKED`; Great Scale PR #128 has no exact-head run and remains `UNKNOWN`. No repository rules, billing settings, or PR merge state were changed.

## References

[1]: https://docs.github.com/billing/managing-billing-for-github-actions/about-billing-for-github-actions "About billing for GitHub Actions"
[2]: https://docs.github.com/articles/what-happens-if-my-repository-is-locked "Unlocking a locked GitHub account"
[3]: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks "Troubleshooting required status checks"
[4]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets "Available rules for rulesets"
[5]: https://api.github.com/repos/doitupsolutions810-crow/great-scale/actions/runs/40392042836/jobs "Great Scale job metadata"
[6]: https://api.github.com/repos/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40406318969/jobs "LICP job metadata"
[7]: https://api.github.com/repos/doitupsolutions810-crow/capability-authority/actions/runs/40223320786/jobs "Capability Authority job metadata"
[8]: https://api.github.com/repos/doitupsolutions810-crow/CycleKernal/actions/runs/40392038552/jobs "CycleKernal job metadata"
