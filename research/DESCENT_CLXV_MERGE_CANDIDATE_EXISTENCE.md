# Descent CLXV — A revision tuple is not a live merge candidate

## Finding

A CI claim can be associated with a pull-request head and base yet still fail to describe the candidate currently offered for integration. The candidate must exist, be based on the exact current head and base, and be the object actually tested. A stale synthetic merge ref is not repaired by correct-looking head/base metadata.

This continues the distinction between a specified rule, an implemented rule, and a verified system. The additional condition is that the object to which verification is bound must be a current, resolvable integration candidate.

## Live Great Scale observation

At the 2026-10-26 inspection of [Great Scale PR #128](https://github.com/doitupsolutions810-crow/great-scale/pull/128), GitHub reported the PR open and draft, with head `8913ce60a8b343739de0dd71cfa435d02732d7ac`, base `101a9b9aa8ff7f71ba6d2ca123190847873a4f2f`, `mergeStateStatus: DIRTY`, and `mergeable: CONFLICTING`. Its check rollup showed a Vercel failure whose URL reports a build-rate limit and a CodeRabbit success; the head had zero GitHub Actions check-runs returned by the queried endpoint.

The fetched `refs/pull/128/merge` object was `6ba76e8ec8356adfd785cc185698e627199073d7`. Its parents were base `101a9b9...` and the older head `3cbe6f0bc20aa10b88afdaa9d220436f4b4d5c4b`, not the current head `8913ce6...`. It is therefore stale for the current PR revision. A local virtual merge of the current head and base produced tree `68865e0082226254dcdab32c469d75e8c5894148` without reporting conflicts, while GitHub's PR metadata reported `CONFLICTING`. Those observations disagree; until the provider recomputes the ref and the exact parents are reconciled, mergeability is **UNKNOWN**, not PASS and not a proven source-code failure.

The current branch's aggregate test command also fails locally before its Python checks: a malformed CommonJS import in `research/topological-qgt.cjs:3` stops `npm test`. After fixing that syntax, the Python descent test had one stale expected value: its formula evaluates `soft_contract(2, 0.5)` to `3.25`, not `3.75`. These are concrete local test blockers, distinct from the merge-ref freshness issue.

## Mathematical contract

Let \(B\) and \(H\) be immutable base and head SHAs. A merge candidate \(M\) is valid for this PR state only if it exists and its ordered parents bind to those exact revisions:

\[
\operatorname{CandidateCurrent}(M;B,H)
=\operatorname{Exists}(M)
\land \operatorname{Parent}_1(M)=B
\land \operatorname{Parent}_2(M)=H.
\]

The candidate is a partial construction: if the merge is conflicting, \(M=\operatorname{merge}(B,H)\) is undefined for the provider's integration procedure. If a merge ref exists but has old parents, it is defined for an earlier pair, not the current pair. A branch name, head SHA, or success attached to an older merge ref cannot substitute for this predicate.

The acceptance rule must therefore include candidate existence and parent binding:

\[
\boxed{
\operatorname{MayPromote}(B,H,M)
\Rightarrow
\operatorname{CandidateCurrent}(M;B,H)
\land \operatorname{WorkflowIdentified}(W)
\land \operatorname{TestsReachable}(W)
\land (\operatorname{RunConclusion}(M,W)=\text{success})
\land \operatorname{PolicyEnforced}.
}
\]

When the merge state is reported conflicting, the action is blocked. When GitHub and an independent local merge computation disagree, the mergeability verdict is unknown until reconciled. Neither condition is an explicit test failure.

## Cross-repository evidence pattern

The same scope mismatch appears in distinct forms across the repositories inspected:

- In [Living Intermediate Control Plane](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane), the local-evidence authorization helper exists and defaults to fail-closed, but `lib/evidence-console.mjs` contains a TypeScript-only `export type` declaration in a `.mjs` module. On the inspected `main` commit, `npm test` and both dry-run procurement modes stop at parse time, before exercising the authorization guard. The policy is specified and visible in source; runtime verification is not established.
- In [Capability Authority](https://github.com/doitupsolutions810-crow/capability-authority), the local CI fallback passed on `0b22ec32…`, while the newest hosted workflow on `integration/evidence-chain-and-index` SHA `7ce3dba…` failed before any test steps were recorded. Local success on another revision cannot certify that integration tip.
- In [CycleKernal](https://github.com/doitupsolutions810-crow/CycleKernal), the Compose monitoring health route returns a successful HTTP response even when MongoDB or Redis readiness strings report `disconnected`. A process-response probe therefore does not establish dependency readiness or end-to-end correctness.

These observations do not imply that the projects share one defect. They demonstrate that each evidence item must name the proposition it supports, the exact subject/revision, and the execution boundary it actually observed.

## Great Scale mapping

| Channel | Meaning | Gate |
|---|---|---|
| \(H,B\) | Immutable candidate inputs | Both exact SHAs must match the reviewed PR state |
| \(M\) | Synthetic merge object | Must exist and have parent SHAs \((B,H)\) in the expected order |
| \(W\) | Workflow definition | Identify the workflow revision that ran |
| \(T(M,W)\) | Test execution evidence | Require reachable tests and a completed success for this exact candidate |
| \(A\) | Server-side authority | Verify policy enforcement separately from local test logic |
| \(\Psi\) | Great Scale scientific scalar | Cannot encode candidate identity or turn stale/absent evidence into verification |

The control-plane evidence envelope should preserve an explicit state: `PASS`, `FAIL`, `BLOCKED`, or `UNKNOWN`. `CONFLICTING` is a confirmed blocker; a stale merge ref or disagreement between provider metadata and a local merge computation is `UNKNOWN` pending reconciliation. A Vercel deployment rate limit is not a failed mathematical test, and a successful CodeRabbit review is not a successful test run.

## Regression integrated

Extended `test_great_scale_cxlix_pr_candidate_binding.py` with two fail-closed cases: a candidate is rejected when mergeability is `CONFLICTING` or unresolved, and a green run attached to a synthetic merge ref with an old head parent is rejected. This is a contract-level regression, not a live GitHub verifier; provider metadata and ref parents still need to be captured and compared by a trusted integration layer.

## Verification boundary and next step

The new regression is part of the existing CXLIX test entrypoint in `npm run all`. In this isolated working copy, I corrected the malformed QGT `require` path and the stale `soft_contract(2)` expected value; the full `npm run all` then exited **0**. Its component output included 20 base Great Scale tests, 14 quantum-geometry bridge tests, 23 topological-QGT tests, 23 descent checks, and all listed Python evidence/authority regressions. `git diff --check` was clean. There is no separate build script in this package.

In a separate local LICP clone at `8510bff…`, replacing the TypeScript-only declaration in `lib/evidence-console.mjs` with JavaScript-compatible JSDoc allowed `npm test` to pass (43 control-plane self-tests and 49 platform tests). Two dry-run procurement checks then distinguished the intended policy: without `ACCEPT_LOCAL_EVIDENCE`, the decision was `READY_LOCAL_HOLD_PUBLIC_EVIDENCE` and `localEvidenceAccepted: false`; with explicit opt-in, it was `READY_FOR_PROCUREMENT` and `localEvidenceAccepted: true`. These edits were tested locally only; they do not change the recorded hosted Actions results.

Hosted verification remains open. The remote synthetic merge ref fetched for PR #128 had the old head as its second parent, and the current PR head had no GitHub Actions check-run in the queried API. A successful hosted Actions run is still required on a newly refreshed candidate whose merge-ref parents match the exact current PR head and base. Do not merge while provider metadata and the actual synthetic merge parents disagree. The local tests establish behavior in these working copies; they do not establish branch protection, provider-side enforcement, or deployment readiness.
