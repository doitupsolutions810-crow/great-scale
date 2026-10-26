# Great Scale — Descent CLXVIII: A green job does not prove the test step ran

## Finding

CLIX constrained the aggregate shell grammar so test files cannot be made unreachable by short-circuit commands such as `false && python3 test.py` or hidden behind `|| true`. CLXVII then improved job-level evidence by distinguishing an account-blocked runner from an executed job. The next descent found a gap between those two layers: the classifier treated any completed green job with a runner and a nonzero step count as `PASS`, without requiring evidence that the designated test step completed.

The current Great Scale workflow contains checkout, Node setup, and `npm run all`. Before this change, a synthetic job with a runner, three steps, and job conclusion `success`—but no designated test-step record—was classified `PASS`. This was reproduced locally against the previous classifier. It is a model-level false positive; it is not evidence that the current hosted workflow actually skipped its tests.

GitHub documents that a skipped job reports `Success`, even when the status check is required. Its workflow-jobs API also exposes individual steps with their own names, statuses, and conclusions. A job-level conclusion therefore cannot, on its own, prove that the canonical test command ran. [1] [2]

## CLXVIII contract

The workflow now gives the aggregate command a stable step identity:

```yaml
- name: Run canonical aggregate
  run: npm run all
```

The existing CI-reachability test checks that this step is named, invokes exactly `npm run all`, and is not guarded by a job/step `if` or `continue-on-error` setting. The evidence model now carries the workflow blob SHA and the designated step’s name, status, and conclusion. A `PASS` requires all of the following: exact head and base; the expected workflow path and matching 40-character workflow-blob identity; the expected GitHub Actions job and pull-request event; an assigned runner and observed execution; the named aggregate step completed with conclusion `success`; and an overall job conclusion of `success`.

An absent or skipped aggregate step is `UNKNOWN`, even if setup steps ran and the job is green. A reported failure from the aggregate step is `FAIL` regardless of the job-level conclusion. The workflow test separately forbids `continue-on-error` on that step. A zero-step job with the explicit account-lock annotation remains `BLOCKED`, not a test failure. The workflow fingerprint and step-name-to-command mapping are contract inputs; this test-only model is not yet an authenticated adapter that collects them from GitHub.

## Great Scale mapping

Let the verification state be

\[
V=(R,B,W,J,S,E,P),
\]

where \(R\) is the exact candidate head, \(B\) the base, \(W\) the workflow blob identity, \(J\) the GitHub job/run, \(S\) the named aggregate step, \(E\) its execution result, and \(P\) the server-side merge policy.

The decision rule becomes

\[
\operatorname{CI\_PASS}=
(R=R^*)\land(B=B^*)\land(W=W^*)\land
(J=\text{expected completed job})\land
(S=\text{Run canonical aggregate})\land
(E=\text{completed success})\land
(J.\text{conclusion}=\text{success}).
\]

Merge acceptance still needs an independent enforcement term:

\[
\operatorname{MayMerge}=\operatorname{CI\_PASS}\land P.
\]

This is distinct from Great Scale’s numerical scalar \(\Psi\): a mathematically correct state score does not establish that the workflow executed the test suite, and local contract tests do not turn themselves into server-enforced policy.

## Deeper system result

The verifier and the thing it verifies currently live in the same changeable candidate. A pull request can alter the workflow, aggregate command, or audit tests together. Without a server-enforced rule or protected ownership of workflow changes, the candidate can weaken its own verification path. This is a trust-root gap, not evidence of malicious behavior.

The live target for PR #128, `research/descent-civ-effect-evidence-boundary`, returned `Branch not protected`; the repository had no `CODEOWNERS` file. The earlier live enforcement audit also found zero rulesets. Because the shared GitHub account remains billing-locked and the current PR head had no eligible hosted check, I did not add merge-blocking rules. The remaining system-level control must be established independently, after a qualifying hosted run exists and the exact check context is known. [3] [4]

## Test, verify, run

The pre-change reproduction returned `pass` for a successful runner-backed job with three steps and no test-step evidence. After the change:

- `python3 test_great_scale_clviii_three_valued_ci_evidence.py` — **11/11 passed**, including setup-only, skipped-test-step, workflow-blob mismatch, explicit billing block, and executed test-step cases.
- `python3 test_great_scale_cxlviii_verification_reachability.py` — **3/3 passed**, including the named, unconditional aggregate-step contract.
- `npm run all` — **passed**, exit code **0**.
- `git diff --check` — exit code **0**.

These are local executions. The pre-change exact PR head `4586a68…` had no hosted check-runs or workflow runs. This integration creates a new PR head, which still requires its own eligible `pull_request` run. Until it is observed, hosted CI remains `UNKNOWN`; no merge or deployment is claimed.

## References

[1]: https://docs.github.com/en/pull-requests/reference/status-checks "Status checks"
[2]: https://docs.github.com/en/rest/actions/workflow-jobs?apiVersion=2026-03-10 "REST API endpoints for workflow jobs"
[3]: https://github.com/doitupsolutions810-crow/great-scale/pull/128 "Great Scale PR 128"
[4]: https://github.com/doitupsolutions810-crow/great-scale/blob/4586a68ed67a223ff5930c59ed4ae5eda2080498/research/DESCENT_CLXVI_LIVE_ENFORCEMENT_AUDIT.md "CLXVI live enforcement audit"
