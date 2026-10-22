# Great Scale Levels 5001–5100 — A fail-closed promotion gate must bind the entire evidence graph

## Analysis

The previous descent isolated an execution-evidence gap: local and hosted test commands are unified, and a receipt is emitted by the command, but no hosted runner has produced executed steps/logs/artifacts. The next step is to formalize a policy that cannot promote a candidate using only a receipt or a success label.

The gate now added on this research branch is `promotion_gate.js`; its adversarial tests are `test_promotion_gate.js`, and they are included in `npm test`.

## Promotion predicate

For candidate repository (P), candidate commit (C), workflow run (R), job (J), receipt (Q), and artifact (A), eligibility for human review requires all these bindings:

[
egin{aligned}
mathrm{Eligible}(C) Rightarrow {}&
R.mathrm{repo}=P land R.mathrm{headSHA}=C land R.mathrm{conclusion}=mathrm{success}\
&land J.mathrm{conclusion}=mathrm{success} land J.mathrm{runnerId}>0\
&land mathrm{logs}(J)
earnothing land mathrm{requiredSteps}(J)=mathrm{success}\
&land Q.mathrm{commit}=C land Q.mathrm{overall}=mathrm{passed}\
&land Q.mathrm{JS}=mathrm{passed} land Q.mathrm{Python}=mathrm{passed}\
&land Q.mathrm{runId}=R.mathrm{id}\
&land A.mathrm{workflowRunId}=R.mathrm{id}land A.mathrm{type}=mathrm{receipt}.
end{aligned}
]

Any missing or contradictory field returns `BLOCKED`. Passing returns `ELIGIBLE_FOR_PROMOTION_REVIEW`, not auto-merge or deployment approval.

Required checks include candidate/run/receipt SHA equality, matching repository, expected CI workflow, successful run and job, observed nonzero runner identity, real job-log URL, all required steps executed successfully (including the receipt upload), passing JavaScript and Python suite outcomes, and a nonexpired artifact belonging to the same run.

## Executed reference tests

The equivalent JavaScript reference harness for the gate passed **29/29 checks**, covering:
- the complete positive fixture produces review eligibility only;
- missing/malformed evidence fails closed;
- altered candidate, run, and receipt SHAs fail;
- failed run/job, zero or missing runner identity, and missing logs fail;
- missing, skipped, duplicate, malformed, or failed steps fail;
- either suite failing in the receipt fails;
- receipt schema, run ID, repository, artifact identity, run binding, and expiry mismatches fail.

These tests exercise equivalent policy logic in the available JavaScript execution tool. They are not execution of the repository's committed `npm test` command. That command includes `test_promotion_gate.js`, but the full repository suite remains unexecuted in the available runtime.

## Trust boundary

The gate deliberately returns `ELIGIBLE_FOR_PROMOTION_REVIEW` rather than `VERIFIED`. It validates relationships in a structured evidence bundle; it does not authenticate the GitHub API collector or prove that submitted fields came from GitHub. A production collector must fetch run/job/artifact metadata through an authenticated GitHub API connection, bind it to the exact candidate SHA, and supply those platform-derived records. A bare JSON field saying `source: github-actions-api` is not authentication.

The local receipt is also not independent attestation. Its purpose is outcome capture. The platform job metadata, logs, and artifact provenance provide the additional execution evidence; checker soundness, test adequacy, independent review, and deployment authorization remain separate gates.

## Actual hosted run status

Latest known hosted execution for the previous candidate failed after retry with no executed step summaries, no logs, and no artifact. The PR head has now advanced again due to the promotion gate and tests. It must be checked afresh for the new exact SHA. The available connector supports re-running failed jobs but does not expose a workflow-dispatch action or runner/billing administration. Re-running a no-runner failure does not create a runner.

Therefore the new gate is integrated and locally reference-tested, but **it is not yet able to accept a real hosted execution receipt** because the required independent platform evidence has not been produced. Keep PR #89 draft and unmerged.

## Mitigation and success criteria

1. Resolve GitHub Actions/Billing diagnostics or use a dedicated ephemeral, least-privilege runner scoped to this repository.
2. Execute the canonical `scripts/verify-local.sh` on the exact candidate SHA.
3. Obtain authenticated platform run/job/step/log/artifact metadata for that same SHA.
4. Pass the evidence bundle to `evaluatePromotionEvidence`.
5. Require the gate to return `ELIGIBLE_FOR_PROMOTION_REVIEW`; then conduct human review and a separate deployment approval.

Never route untrusted PR code to a privileged cross-repository runner with a Docker socket. Do not confuse a gate test passing with the candidate's product tests passing.

## Greater profound finding

**Promotion is not a scalar score; it is a conjunction over a provenance-bound evidence graph.** A strong claim cannot compensate for a missing runner; perfect logs cannot compensate for a stale SHA; and a correct receipt format cannot authenticate its own author. The weakest missing edge blocks the conclusion, rather than lowering a numeric confidence score that might still cross a threshold.

This is a software-assurance result and research policy. It is not a new physical law of quantum geometry.
