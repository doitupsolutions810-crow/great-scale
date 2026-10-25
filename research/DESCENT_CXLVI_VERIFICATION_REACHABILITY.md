# Descent CXLVI — verification reachability is part of the proof

## Finding

A test that exists in a repository is not a verified invariant unless the canonical test command reaches it. Treat test reachability as a separate proof obligation:

\[
\operatorname{Verified}(P) \Rightarrow
\operatorname{Specified}(P) \land
\operatorname{Executed}(P,\,\text{tested revision}) \land
\operatorname{ObservedResult}(P)
\]

A source-level assertion, a local model run, a package script, and a hosted CI result are different evidence classes. They must not be collapsed into one green status.

## Repository evidence at the inspected Great Scale head

Before this descent:

- `package.json` exposed `npm test` for the Node tests.
- Its aggregate `all` script referenced `test_evidence_triad.py`, which was absent from the inspected repository tree, and did not invoke `test_great_scale_cxlv_atomic_projection.py`.
- `.github/workflows/ci.yml` ran `npm test` and `python3 test_descent.py`; it did not run the effect/evidence boundary model or the CXLV ledger/projection model.
- The CI workflow's pull-request trigger was filtered to PRs whose base is `main`. Great Scale PR #128 targets `research/descent-civ-effect-evidence-boundary`, not `main`.

Therefore, the existence of the model files did not establish that the canonical workflow executed them. In addition, a workflow edit present only in a PR head is not proof that this branch-to-branch PR will use the new trigger configuration; the base branch's workflow definition controls whether the pull-request event starts a run.

## Integration made

The branch `research/descent-cxli-evidence-projection-reconciliation` now changes:

1. `package.json`: the aggregate `all` script removes the nonexistent `test_evidence_triad.py` reference and explicitly runs both `test_effect_evidence_boundary.py` and `test_great_scale_cxlv_atomic_projection.py`.
2. `.github/workflows/ci.yml`: the job invokes `npm run all`, making the aggregate command the single canonical CI entry point and preventing those model tests from being silently omitted by the old workflow command list.

This fixes the source-level command graph. It does not, by itself, prove a hosted run occurred or passed.

## Great Scale mapping

Let (T\) be the set of required test programs, (C\) the command graph reachable from the canonical CI entry point, and (R\) the exact revision tested. Test coverage requires:

\[
T_{\mathrm{required}} \subseteq \operatorname{Reachable}(C)
\]

A green result is meaningful only when the run's tested revision equals the reviewed revision:

\[
\operatorname{AcceptCI}(R) =
\operatorname{Reachable}(T_{\mathrm{required}}, C)
\land \operatorname{RunHead}=R
\land \operatorname{Conclusion}=\text{success}
\]

A green run on another SHA, or a passing model never invoked by CI, does not discharge the proof obligation.

## Verification status

- Source integration: committed on the PR branch; inspect the current head and workflow run list before treating it as active.
- Local execution of the newly modified aggregate command: not performed in this connector-only step.
- Hosted CI on the new head: not yet verified.
- PR #128 remains a draft and unmerged.
- No build, deployment, or production validation is claimed.

## Next required checks

1. Run `npm run all` from a clean checkout of the exact new head.
2. Ensure the base branch's workflow configuration permits the branch-to-branch PR to trigger CI, or run a trusted manual workflow on that exact SHA.
3. Record each required test command, exit code, run URL, and exact tested SHA.
4. Keep model/contract tests labeled as models unless they exercise the actual production implementation and concurrency boundaries.

## Profound conclusion

Verification is not just a property of code or tests. It is a property of the path from a stated invariant, through an executable test, into a run bound to an exact revision, with an observable result. If that path is broken, the system has an evidence gap even when every individual test file looks correct.
