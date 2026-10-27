# Cross-Repository Verification and Promotion Plan

Status: proposed engineering contract; not evidence that dependent PRs have passed.
Audit date: 2026-10-26.

## Purpose

Coordinate promotion across Great Scale, Living Intermediate Control Plane (LICP), CycleKernal, and Capability Authority without treating a green advisory check, a syntactically valid evidence record, or a model-derived scalar as proof of end-to-end correctness.

## Trust and data flow

```mermaid
flowchart TD
  GS[Great Scale\nmathematical model, QGT, descent evidence]
  LVI[Living Intermediate Control Plane\nauthenticated ingress, schema, admission]
  CA[Capability Authority\ncapability policy, signing, operation ledger]
  CK[CycleKernal\nsimulation, relay, execution and lineage]
  REC[Reconciliation and promotion gate]
  GS -->|schema + commit-bound model evidence| LVI
  LVI -->|authenticated principal + validated request| CA
  CA -->|method-bound capability + operation identity| CK
  CK -->|observed execution receipt + lineage| CA
  CA -->|signed durable receipt| LVI
  LVI -->|integrity + authenticity + authority + revision check| REC
  GS -->|QGT numeric diagnostics + mathematical test evidence| REC
```

Arrows express required trust dependencies, not proof that every integration is currently implemented.

## Required acceptance predicate

A promotion consumer should independently validate all of the following:

`Accept(e) = Integrity(e) AND Authenticity(e) AND Execution(e) AND Authority(e) AND RevisionBinding(e)`

- **Integrity:** canonical serialization and digest/signature cover the complete accepted payload.
- **Authenticity:** issuer identity chains to an explicitly provisioned trust anchor. A hash alone does not authenticate an issuer.
- **Execution:** evidence is tied to an actual run/job and observed outcome, not merely an intended operation.
- **Authority:** the issuing principal had rights for the exact resource and method, under valid constraints and expiry.
- **Revision binding:** repository, full commit SHA, workflow run/job IDs, and produced artifact digest match the candidate being evaluated.

These checks are conjunctive. They must not be collapsed into a single ambiguous boolean without preserving reasons and provenance for each sub-result.

## Merge dependency order

1. **Baseline and CI observability.** Record each repository's default-branch SHA and PR base/head SHAs; restore workflow job-step and log access. A failed job with no steps is an infrastructure/verification blocker with an unknown cause, not proof that code assertions failed.
2. **Local security gates.**
   - LICP #23: bearer parsing, tokenless non-loopback bind refusal, sensitive route auth.
   - Capability Authority #5: exact `(type, resource, method)` matching; method-bound rate limit and receipt identity.
   - Capability Authority #7: explicit least-privilege issuance allowlist.
   - Capability Authority #8/#9: provisioned signing key and fail-closed startup validation.
3. **Execution/evidence durability.** Capability Authority #12 must provide durable event identity, concurrency-safe append, safe replay, corruption detection, and reconciliation. Stable event IDs do not alone guarantee exactly-once external side effects.
4. **Cross-repository admission.** LICP #15/#20 and Great Scale #124/#126/#128 should use one versioned envelope and exact revision identity. Structural validation is not a cryptographic trust gate.
5. **CycleKernal execution provenance.** CycleKernal #9 must pass its actual compile, simulation, relay parser, lineage, and container-build workflow. No syntax fix should be introduced unless an exact file/line failure is reproduced.
6. **Mathematical/numerical promotion.** Great Scale #116 and #122 need exact-head numerical and quotient regression results, including extreme-scale representability. Downstream evidence consumers must handle nullable raw determinants and their explicit statuses. For the evidence stack, evaluate #127 (side-effect/acknowledgement boundary) before #128 (projection/idempotency reconciliation).
7. **End-to-end promotion.** Run failure injection, replay, authorization mismatch, stale-revision, cross-language parity, and reconciliation scenarios against pinned candidate commits. Only then consider merge order and deployment.

## PR map (review pointers; status must be refreshed at promotion time)

| Repository | PR | Required gate |
|---|---:|---|
| Living Intermediate Control Plane | [#23](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/23) | Bearer parsing plus route/network auth regressions and inspectable exact-head CI |
| Capability Authority | [#5](https://github.com/doitupsolutions810-crow/capability-authority/pull/5) | Method-bound authorization, receipt identity, rate-limit tuple |
| Capability Authority | [#7](https://github.com/doitupsolutions810-crow/capability-authority/pull/7) | Rights allowlist enforced at issuance |
| Capability Authority | [#8](https://github.com/doitupsolutions810-crow/capability-authority/pull/8) | Key provisioning, file safety, no silent production regeneration |
| Capability Authority | [#9](https://github.com/doitupsolutions810-crow/capability-authority/pull/9) | Startup/readiness integration for key and policy validation |
| Capability Authority | [#12](https://github.com/doitupsolutions810-crow/capability-authority/pull/12) | Durable ledger and fail-closed evidence index with replay/recovery tests |
| Living Intermediate Control Plane | [#15](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/15) | Authenticated CycleKernal provenance |
| Living Intermediate Control Plane | [#20](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/20) | Structural validator only; cryptographic verifier remains separate |
| CycleKernal | [#9](https://github.com/doitupsolutions810-crow/CycleKernal/pull/9) | Actual Python compile, test suite, relay tests, and both images |
| Great Scale | [#116](https://github.com/doitupsolutions810-crow/great-scale/pull/116) | Compensated QGT, eigenvalue conditioning, explicit raw determinant status |
| Great Scale | [#122](https://github.com/doitupsolutions810-crow/great-scale/pull/122) | Quotient fiber invariance distinguished from seam continuity |
| Great Scale | [#124](https://github.com/doitupsolutions810-crow/great-scale/pull/124), [#126](https://github.com/doitupsolutions810-crow/great-scale/pull/126) | Evidence classification and acceptance contract |\n| Great Scale | [#127](https://github.com/doitupsolutions810-crow/great-scale/pull/127) → [#128](https://github.com/doitupsolutions810-crow/great-scale/pull/128) | Side-effect / acknowledgement boundary precedes projection reconciliation; refresh the stack because #128's reported base SHA differed from #127's current head SHA during this review |

This table describes dependencies and verification requirements, not confirmed merge readiness. Observed stack facts on 2026-10-26: CycleKernal #9 targets `feature/great-scale-descent-wire`, whose head matches CycleKernal #1's reviewed head. Capability Authority #9 targets `fix/provisioned-signing-key-production`, whose head matches Capability Authority #8's reviewed head. Great Scale #128 names the PR #127 branch as its base, but its recorded base SHA (`101a9b9aa8ff7f71ba6d2ca123190847873a4f2f`) differs from PR #127's current reviewed head (`f93b5d7520ae9a483a30ed77d8fa952fd6003a71`). Reconcile that divergence before treating the stack as current. Branch ancestry and ahead/behind counts must be refreshed before promoting stacked PRs.

## Operation idempotency and recovery contract

An evidence event and an external side effect are different identities. For an action, require a stable operation ID and canonical request digest. A retry with the same ID and same digest must resolve to the original outcome or an explicit indeterminate state; a retry with the same ID and a different digest must be rejected.

If an external side effect may have committed but its acknowledgement is lost, the system must reconcile authoritative state before retrying. A unique event ID prevents duplicate evidence records; it does not make a non-idempotent side effect execute exactly once.

Prefer one transactional source of truth (for example, a SQLite ledger with projections derived from it), or a durable outbox with sequence/watermark and reconciliation. A process-local lock and atomic JSON rename do not prevent stale writers in other processes.

## QGT numerical contract

The QGT bridge accepts only finite numeric inputs and a positive-definite two-direction metric. Tests should use actual binary64 input values as the high-precision reference input, not idealized decimal strings.

- For a symmetric metric `G = [[a,b],[b,d]]`, verify `det(G) = ad - b²`, positive eigenvalues, and `lambda_min = det(G)/lambda_max` where applicable.
- Check `chi = |F12|/(2 sqrt(det(G)))` and its accepted boundary/tolerance policy.
- Verify common scaling `(G,F) -> (sG,sF)` preserves normalized curvature and shape diagnostics.
- A raw determinant outside binary64 range must not be emitted as Infinity or silently mapped to zero. Return `null` plus `detGStatus`/`detQStatus` (`overflow`, `underflow`, `finite`) and require consumers to inspect the status.
- Add near-singular sweeps, subnormals, overflow/underflow, invalid metrics, non-finite input rejection, deterministic randomized metamorphic tests, and JavaScript/Control Plane parity checks.
- Do not treat the Great Scale scalar mapping as an experimentally established physical law; keep formal derivation, numerical observations, and physical hypotheses separately labeled.

## Failure-injection release gate

Before any closed-loop privileged operation is enabled, test at least:

1. Commit external effect, then lose its acknowledgement before receipt persistence.
2. Two concurrent submissions with the same operation ID.
3. Same operation ID reused with a different request digest.
4. Missing, unsafe, or rotated signing key during startup/runtime.
5. Correct resource but wrong capability method.
6. Expired, replayed, or revoked capability.
7. Corrupted evidence index, restart, and reconciliation.
8. Stale CI evidence after the PR head changes.
9. Duplicate JSON keys, conflicting aliases, non-finite values, and invalid relay envelope.
10. QGT scales and near-singular cases at representability limits.

Record the exact commit SHA, command, exit code, test output, workflow/run/job identity, and artifact digest. If logs or runner steps are absent, mark that gate blocked, not passed.

## No-merge rule

This plan does not authorize merging a PR merely because a dependent PR exists or an isolated test passes. Merge readiness requires inspectable CI on exact heads, fulfilled dependency gates, human review of production rights/configuration, and no unresolved critical or high-severity finding.

## Observed check snapshot (2026-10-26; refresh before any promotion)

| Repository / candidate | Directly observed check evidence | Interpretation |
|---|---|---|
| Great Scale #116 — `2bfd05bc886dfcd62970d403b3fd36a2ba68ab52` | Combined status: Vercel failure with target URL indicating `build-rate-limit`; CodeRabbit success. Actions run [40412744540](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40412744540) is failed; latest job has no step list/log blob. | Vercel preview is rate-limited; Actions cause remains unknown. Neither proves a numerical test assertion failed or passed. |
| LICP #23 — `7a399642790f259624a2ce2e9309be868625592b` | Combined status: Vercel `build-rate-limit` failure; CodeRabbit success; Snyk status success. Plane CI run [40411279314](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40411279314) reports the verification job failed, but step/log retrieval returns no blob. | Static/security advisory checks are not the platform test suite. Root cause of Plane CI failure remains unknown. |
| CycleKernal #9 — `d82f381f6ab1408f40aa11e8268ee6c8fc0238c8` | Combined status reports Snyk success and CodeRabbit success. Actions run [40392038552](https://github.com/doitupsolutions810-crow/CycleKernal/actions/runs/40392038552) reports failure without inspectable executed-step evidence. | Advisory checks do not replace Python compile, relay/simulation tests, or image builds. |
| Capability Authority #5 — `51d881f8be22761666d4dbadd19909a50cd3b643` | Combined status reports Snyk success and CodeRabbit success. | No full-suite result was established by this status snapshot. |

The Actions log download for Great Scale and LICP returned `BlobNotFound`; job payloads contained no step summaries. Treat this as an observability/verification blocker. Do not infer the underlying code failed, and do not infer the suite passed. A failed Vercel status whose target explicitly says `build-rate-limit` should be handled as preview-infrastructure quota, separately from unit-test results.

## Immediate operational actions

1. Restore or enable inspectable Actions logs/job steps; if the failure is transient, run a fresh workflow on the exact current head and retain artifacts.
2. Resolve the Vercel build-rate-limit through the repository's deployment owner/quota settings or disable only the non-required preview check by an explicit repository policy decision. Do not weaken test/security gates to obtain a green badge.
3. Run Great Scale `npm test` and `npm run all` on a full checkout of the pinned candidate SHA; record actual shell exit codes and raw output.
4. Run LICP's declared verification/test workflow on the pinned head and inspect its failing job logs before assigning a code root cause.
5. Run CycleKernal compile, unit tests, relay/simulation tests, and container builds at its current exact head.
6. Re-check the full Capability Authority PR stack and durable-ledger tests; Snyk/CodeRabbit green is not evidence for authorization correctness, key lifecycle, or crash consistency.


## Descent CLXXXIX — shared operation/evidence contract

The candidate contracts now have a common reference: [Operation and Evidence Contract v1](OPERATION_EVIDENCE_CONTRACT_V1.md). This unifies the intended meaning of stable operation identity, per-service canonical request digest, parent correlation, durable intent, observed effect, receipt read-back, and the `indeterminate` state.

The proposed integrations are still separate draft changes:
- LICP #34 bounds and verifies the transport of a configured production-attestation document; it does not deploy a trusted producer or provision signing keys.
- Capability Authority #12 adds operation-level intent/receipt persistence and prevents blind re-execution under the same operation ID after an uncertain effect.
- CycleKernel #13 adds idempotent MongoDB chat persistence and separates ancillary Redis/metrics failures from the primary write result.

Each candidate has its own local isolated tests, but the hosted runners in this account have failed before recording any steps. None of the above edges is end-to-end verified or ready for production promotion. The common contract is a success criterion for the next integration suite, not a claim that the individual services already exchange one canonical envelope.


## Descent CXCIX — G0-G6 consumer contract alignment

**Status: proposed consumer contract; no authoritative G0-G6 producer or end-to-end acceptance run has been verified.**

Living Intermediate Control Plane PR [#34](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/34) now carries a candidate proof-carrying production-attestation contract:
- `contracts/production-acceptance/v1.schema.json` defines source/revision, workflow run/attempt, artifact digest, suite results, G0-G6 evidence, residual, digest, and signature fields.
- `contracts/production-acceptance/gate-policy-v1.json` maps G0-G6 to versioned policy IDs and named evidence suites.
- `lib/production-acceptance-attestation.mjs` verifies the signed structure, exact source/run/build/artifact pins, required suite set, per-gate suite evidence, residual freshness, policy version/digest, and Ed25519 signature.
- `lib/production-acceptance-fetch.mjs` bounds and hardens the network boundary.

These files are on an **unmerged draft branch**. They are a consumer-side contract and verifier candidate, not proof that Great Scale, CycleKernal, or a deployed producer currently emits the artifact. The policy’s seven suite names are proposed semantics; they must not be treated as existing passed workflows until the producer verifies real runs and evidence.

### Release proof obligations

For this system, the relevant obligations are conjunctive:

- **M — Manifest completeness:** every required repository/module and acceptance suite is explicitly enumerated; no required test is omitted.
- **R — Test reachability:** the committed test runner demonstrably invokes the assertions, rather than merely listing a Python file or checking that it exists.
- **E — Execution evidence:** test/workflow evidence shows a real runner, executed steps, observed conclusion, and inspectable result. A runnerless failure with zero steps is `UNKNOWN/BLOCKED`, never `PASS`; it is also not proof that source assertions failed.
- **P — Provenance:** all evidence is tied to the exact repository, full source commit SHA, workflow run and attempt, artifact digest, and independently provisioned signer identity.
- **A — Authority:** the signer and action are independently authorized; public availability or an opted-in local fallback cannot silently widen permission.
- **F — Freshness:** the run, source evidence, attestation and residual measurement satisfy the configured timestamp/expiry policy.
- **B — Boundary separation:** E0-E6 source-contract checks are not relabeled as G0-G6 production acceptance; procurement readiness is not production authorization.

A candidate is eligible for promotion only when each obligation is independently satisfied:

```text
Promote = M AND R AND E AND P AND A AND F AND B
```

The G0-G6 policy documents intended criteria for source binding, required CI, immutable artifact provenance, supply-chain attestation, security policy, runtime health, and residual measurement. It does not establish those criteria as true merely by naming the gates or signing a document.

### Current integration disposition

- Great Scale public registry: 14 public repositories and 5 proposed interfaces; all interface statuses remain `proposed-not-verified`.
- Full account inventory: maintained separately in private CONTROL12 PR [#32](https://github.com/doitupsolutions810-crow/control12-lattice-ops/pull/32); 35 records / 9 proposed interfaces, not runtime proof.
- LICP G0-G6 contract: [PR #34](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/34), draft and unmerged.
- Hosted CI evidence currently available for the latest LICP candidate is still failing before any test steps are recorded. The provider-level cause is not exposed through the available job/log data. Vercel's build-rate-limit failure is a separate preview constraint.

### Next acceptance step

The producer connection remains the last unconnected trust boundary. Implement it only where the evidence originates: the producer must fetch/validate the actual run and required suite outcomes, bind the verified artifact and residual to the same build/revision, then sign with an independently provisioned key. The consumer must independently verify the pinned identity and contract. The edge may be marked `verified` only after exact-head hosted CI executes with inspectable passing steps and live positive/negative integration tests pass. Until then: **HOLD / NO-GO**.


## Descent CC — Shared hosted execution blocker (2026-10-27)

A fresh exact-head check across the candidate repositories shows the same evidence pattern: GitHub reports the workflow job as failed, but the job has no executed steps, no runner assignment (`runner_id: 0` where exposed), and no downloadable log blob. That makes the source test result **UNKNOWN/BLOCKED**, not pass and not a demonstrated code assertion failure.

| Candidate | Exact head SHA | Workflow run | Observed job state |
|---|---|---|---|
| Great Scale PR #129 | `636dc6ff6cd0aaec065f5451875c97ea88044e45` | [#40451340121](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40451340121) | `failure`, no step list |
| LICP PR #34 | `3a9c43e9122b92a6bfcdc282478d5afae6fe86b5` | [#40451230072](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40451230072) | `failure`, no step list |
| LICP Plane CI | `3a9c43e9122b92a6bfcdc282478d5afae6fe86b5` | [#40451230049](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40451230049) | verification job has no step list; dependent container job skipped |
| Capability Authority PR #12 | `dd8c4e38136d3e3e81891045be0ace216a6c5253` | [#40429217283](https://github.com/doitupsolutions810-crow/capability-authority/actions/runs/40429217283) | both jobs `failure`, no step lists |
| CycleKernal PR #9 | `be0d13764ee3ff4e8d4e60a24cc1f446d9631126` | [#40417726051](https://github.com/doitupsolutions810-crow/CycleKernal/actions/runs/40417726051) | `failure`, no step list |

The available job/log interface does not expose the provider's precise cause. Do not infer billing lock, source failure, or a green result from this evidence. Vercel separately reports a build-rate-limit failure for preview deployments; that does not explain the runnerless Actions jobs.

### Mitigation decision

- Preserve all CI and authorization gates; do not weaken the test requirement to obtain a green badge.
- Keep the contract and inventory PRs draft while hosted execution remains unavailable.
- Treat the isolated local harnesses as limited unit evidence only. They cannot satisfy **E — observed execution evidence** or **P — exact revision provenance** for promotion.
- Ask the GitHub account/repository owner to inspect the Actions UI or GitHub Support for the exact runner initialization annotation. The integration tooling available in this session cannot retrieve that annotation or alter account-level Actions settings.
- After the runner issue is resolved, rerun the focused and full suites at the exact current SHAs; retain run/job IDs, step logs, suite results, artifact digests and the source SHA in the promotion evidence.

The cross-repository integration status remains `proposed-not-verified`. The G0-G6 policy is a consumer contract only until an authoritative producer emits a fresh signed proof and all of M, R, E, P, A, F and B pass.
