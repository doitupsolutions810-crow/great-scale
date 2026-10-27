# Descent CLXXIX — Validator Totality and CI Observability

Date: 2026-10-26 / repository timestamps are UTC and may show 2026-10-27.

## Finding

A fresh source-level audit of control-plane PR #33 found two concrete defects in the evidence-console test/validation path:

1. `validateEvidenceConsoleContract` referenced `required.includes(...)` before the later `const required = schemaDocument.required` declaration. Because `const` is in the temporal dead zone, any ordinary schema with a properties object could throw a `ReferenceError` instead of returning structured validation failures.
2. `test/evidence-console.test.mjs` contained a duplicated stale block of 237 lines. The second copy repeated earlier tests without the current trust options and carried an outdated schema fixture, making the suite contradictory with the new Ed25519 fail-closed contract.

## Mitigation committed to control-plane PR #33

- Commit `c5fbe769c98ecc57aea9504d735c2cbf8a9faa74`: initializes the schema-required list before property checks and removes the later temporal-dead-zone declaration. Missing/non-array `schemaDocument.required` now produces structured contract failures instead of an unhandled reference error.
- Commit `5b2fe6e9c4e4355753d97b6d3a6f1047e0c836f9`: removes the duplicate stale test block while preserving the current cryptographic tests.
- Commit `6b92aeeb2c843ee9d90056d9ca74cf9561e9ef25`: adds a regression test for a missing schema `required` list, asserting a structured invalid result and no throw.

PR: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/33

## Verification status

Static verification confirms the source now declares the required list before use, the test file has one copy of the primary contract test, and the missing-required regression test is present on the current branch head `6b92aeeb2c843ee9d90056d9ca74cf9561e9ef25`.

Hosted verification is **not passed**. The workflow run for this exact head (`40439149122`) was retried (attempt 2) and again failed within seconds. Both attempts report `runner_id: 0`, zero executed steps, no job log URL, and two check annotations whose payloads are not exposed by the available connector. This is consistent with a workflow/runner initialization failure, but the precise cause is not available, so it cannot be conclusively diagnosed. It does not establish whether the test suite passes. A clean checkout and executable local test run remain unavailable in this environment. Do not report CI green.

## Great Scale authorization mapping

Let:
- (V): validator returns structured outcomes for malformed/missing schema fields (totality),
- (T): HTTPS endpoint binding and redirect protection,
- (C): exact versioned status/schema contract,
- (F): source timestamp freshness/expiry checks,
- (K): pinned source identity and key ID,
- (D): recomputed canonical SHA-256 digest matches,
- (S): Ed25519 signature verifies,
- (G): exact required G0–G6 gate coverage/readiness,
- (I): producer and consumer have an integration-tested, identical signing contract,
- (H): successful hosted workflow on the exact candidate head.

Then consumer-side public evidence authorization must require:

`A_{public} = V \land T \land C \land F \land K \land D \land S \land G \land I \land H`

The newly committed changes address (V) and remove stale tests, but do not establish (H) or (I). Code presence is not test evidence; test fixtures are not a deployed producer; HTTPS is not a signing trust anchor.

Production authorization remains HOLD until the exact-head CI run actually executes and passes, and the real producer/key configuration and canonicalization contract are verified. No production key or authority was invented or enabled.


## CLXXIX.1 follow-up — cleanup patch itself required a syntax audit

A subsequent re-read of the current test file found that the duplicate-block cleanup had left a 1,312-character orphaned tail of the old `goodSchema` fixture between the remaining tests and the cryptographic tests. This was an additional concrete defect introduced by the cleanup edit, not a CI diagnosis. Commit `58712965e93a2c4cc63113553db14faafd49dab0` removes that orphaned fragment. Static re-fetch then confirmed the test file has 396 lines, exactly one primary contract test, exactly one signed-evidence happy-path test, no orphan marker, and the missing-required regression test at the end.

The workflow for that exact head (`40439627571`) again failed within seconds with `runner_id: 0`, no step list, and no job log URL. Because the runner did not expose an executed step, this still cannot establish that Node parsed or ran the test file. This sequence demonstrates why source edits and CI execution need separate evidence: a source-level cleanup can itself introduce a syntax defect, and an opaque runner failure cannot detect or clear it.

Updated authorization rule: treat test-source integrity as a separate gate, (X), where (X) means the exact checked-in test files parse and execute in a real runtime. Require:

`A_public = V ∧ T ∧ C ∧ F ∧ K ∧ D ∧ S ∧ G ∧ I ∧ X ∧ H`

Current evidence establishes static shape checks only; (X) and (H) remain unverified. Production HOLD remains mandatory.


Latest retry for control-plane head `58712965e93a2c4cc63113553db14faafd49dab0`: run `40439627571`, attempt 2, again completed as failure with no steps and no job log URL (`runner_id` unavailable through this job response). The retry was explicitly requested after the orphaned test fixture was removed; it still did not expose executable verification. The environment/runner fault remains an unresolved blocker, not evidence of test success or a source-level test failure.


## CLXXX follow-up — the producer exists, but it is the wrong authority domain

A deeper repository-tree inspection located `lib/evidence-status-document.mjs` and `status/evidence-status.mjs` on the control-plane candidate. This narrows the earlier producer gap: there is a real local evidence-document producer, but it is explicitly a **procurement / E0–E6** producer, not a G0–G6 production-status endpoint.

Its wire contract is incompatible with the new consumer contract:

- Producer fields: `schema`, `generatedAt`, `expiresAt`, `contractChecks`, `namespaces`, `digest`, `keyId`, `signature`.
- Consumer requires: `sourceGeneratedAt`, `sourceExpiresAt`, `gates`, `sourceIdentity`, `sourceKeyId`, `sourceEvidenceDigest`, `sourceSignature` and a production-ready G0–G6 gate set.
- Producer digest is SHA-256 of canonical JSON body and its Ed25519 signature covers the canonical JSON payload bytes.
- Consumer digest is SHA-256 of canonicalized status with digest/signature fields omitted, then Ed25519 verifies the 32 digest bytes.
- Producer explicitly reports `productionClaimed: false` from its verifier and documents that it does not claim production authorization.

This is not merely a missing endpoint URL. It is a deliberate trust-domain boundary and a cryptographic protocol mismatch. Relabeling E0–E6 checks or copying field names would be an unsafe bridge. Keep procurement evidence and production authorization separate. A future production producer needs its own explicit G0–G6 contract and signing profile, with independently pinned identity/key and an end-to-end integration test.

A regression test was added in control-plane commit `3004707d31b4928c58a6fa3ca8b02981aa9b810a`: a signed E0–E6 producer document must be rejected by the production consumer and cannot yield public authority. This test is committed but not runtime-verified because hosted CI continues to fail without exposing executed steps or logs.

Updated rule: `A_public = V ∧ T ∧ C ∧ F ∧ K ∧ D ∧ S ∧ G ∧ I ∧ X ∧ H ∧ P`, where (P) means the signed payload came from the explicitly authorized producer/domain (not merely a producer that can sign something). The current local producer establishes procurement evidence only; (P) for production remains false/unverified. Production HOLD remains mandatory.


### CLXXX latest exact-head retry

The new procurement-to-production boundary regression is committed at control-plane head `3004707d31b4928c58a6fa3ca8b02981aa9b810a`. Its workflow run `40440181670` was retried (attempt 2) and again failed without exposed steps or logs; the container job was skipped after the first job failed. The combined commit status also shows Snyk success but Vercel failure due a build-rate-limit URL. Neither status proves the Node test suite executed. The producer/consumer protocol mismatch is now documented and a regression test is present, but that test remains unexecuted in the available evidence. Keep the pull requests in draft and production HOLD.


## CLXXXII — capability-plane evidence is an integrity trail, not yet a production attestation

Cross-repository descent into `doitupsolutions810-crow/capability-authority` located production-relevant controls, but not a ready-made G0–G6 signed status producer:

- `rings/production_profile.py` defines a production preflight around SPIRE workload identity, rejecting `dev:*` measurements, and forbidding caller override.
- `rings/supply_chain.py` currently defaults to `sha256:dev-placeholder-broker` and `sha256:dev-placeholder-executor`; these are development placeholders, not production pins.
- `evidence/warehouse.py` computes a SHA-256 hash chain over canonical JSON events and can verify chain continuity. It does not authenticate the producer: no Ed25519 source signature or pinned producer identity is added by this module.
- `evidence/index.py` catches any warehouse append exception and continues indexing the event. This is acceptable for best-effort indexing, but it cannot be treated as a mandatory production evidence path.
- The current receipt path signs capability/receipt payloads with a locally loaded/generated broker key; this is not yet demonstrated to be the same independently pinned identity/key used by the evidence-console consumer.

This narrows the remaining integration gap: a traceable evidence store and signed execution receipts exist, but those primitives do not themselves establish a production-ready G0–G6 attestation. Hash-chain integrity answers “was this record altered relative to the chain?”; a source signature plus pinned identity answers “which trusted producer vouched for this record?”; production gates answer “were the required controls actually satisfied?” These are three distinct predicates.

### Required integration sequence

1. Remove development-placeholder supply-chain pins from the production acceptance path; require immutable, verified image digests.
2. Run production preflight using live SPIRE Workload API identity, non-development measurement, and caller override disabled.
3. Derive G0–G6 statuses from concrete checks/receipts, not caller-provided booleans or a relabelled E0–E6 document.
4. Bind each accepted evidence record to the producer identity and key ID; verify the signed payload under an independently pinned public key.
5. Make warehouse append/verification failure fatal for the production evidence path (the best-effort index may remain non-authoritative).
6. Publish a versioned G0–G6 status endpoint only after all above checks pass, then run end-to-end positive, tamper, stale, wrong-key, wrong-identity, missing-gate, and procurement-domain rejection tests.

This is a proposed integration checklist derived from the inspected implementations, not a claim that these mappings are already implemented. No production G0–G6 producer or deployed trust binding was found in the inspected source. Production remains HOLD.


## CLXXXVI — producer/consumer protocol mismatch is a trust boundary

Added [Descent CLXXXVI](https://github.com/doitupsolutions810-crow/great-scale/blob/research/descent-cxli-evidence-projection-reconciliation/research/DESCENT_CLXXXVI_PRODUCER_CONSUMER_PROTOCOL_MISMATCH.md) after re-reading the actual control-plane producer, consumer, namespace evaluator, and regression test.

The producer emits signed E0–E6 procurement evidence using canonical-JSON payload bytes and explicitly reports `productionClaimed: false`. The consumer requires a different status shape, G0–G6 readiness, independently pinned identity/key ID, and an Ed25519 signature over the 32-byte canonical status digest. The mismatch is in the authority domain and signed-message protocol, not just field names. A relabeling adapter would not prove production authority.

The regression test that rejects procurement evidence as G0–G6 authority is present at control-plane PR #33 head `3004707d31b4928c58a6fa3ca8b02981aa9b810a`; it remains source-verified, not runtime-verified. The corresponding exact-head workflow run `40440181670` failed without exposing executed steps/logs. Vercel's build-rate-limit failure and Snyk success do not establish test execution.

Formal release predicate:

`A_prod = I ∧ M ∧ G ∧ F ∧ C ∧ X ∧ L`

where (I) is independent producer identity, (M) is protocol/signature agreement, (G) is authoritative G0–G6 evidence, (F) is freshness, (C) is exact contract binding, (X) is observable exact-revision test execution, and (L) is live endpoint/key verification. Procurement-document validity alone does not imply any of these production predicates.

Decision remains **HOLD**. The note is a documented finding and integration sequence, not a production producer implementation; PR #33 and PR #128 remain draft.


## CLXXXVII — isolated CI still fails before runner steps

Added [Descent CLXXXVII](https://github.com/doitupsolutions810-crow/great-scale/blob/research/descent-cxli-evidence-projection-reconciliation/research/DESCENT_CLXXXVII_ISOLATED_CI_PRE_RUNNER_FAILURE.md).

A focused, read-only GitHub Actions workflow was committed to control-plane PR #33 at `1b2ad196dc6dfd6c6b23083fed5d8238700997da`. It isolates Node 20 syntax checks and the evidence/namespace regression tests from the wider Docker/security pipeline. The workflow triggered at [run 40441231142](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40441231142), but failed within seconds with no steps, no runner identity, and no downloadable logs. The existing Plane CI run at the same SHA has the same zero-step pattern.

This is not evidence that the tests failed; it is also not a pass. The exact pre-runner cause is not exposed in available metadata. The next mitigation is to inspect repository/account Actions runner availability and execution policy. Production remains HOLD until test steps execute visibly and live production trust binding is independently verified.


### CLXXXVII follow-up — retry did not reach runner

Retried the focused workflow once after the initial zero-step failure. GitHub accepted the retry, but the new job `121982755664` again completed as failure with an empty steps list. Repository metadata shows owner admin permission, but the available integration cannot inspect or change Actions runner availability, policy, or usage limits. No settings were changed. The root cause remains unconfirmed and further identical retries are not useful until Actions execution is restored. Production remains HOLD.


### CLXXXVIII — overlapping PR history reconciliation

Control Plane PR #31 is reported `mergeable: false`; PR #33 is reported `mergeable: true`. Their branches diverge (comparison reports 38 ahead / 65 behind) and both touch `lib/evidence-console.mjs`, `test/evidence-console.test.mjs`, `package.json`, and `status/procurement-bridge.mjs`. Do not merge them independently or blindly rebase. Select one integration base, reconcile the overlapping implementation and tests, then test the exact combined SHA. GitHub's mergeability flag is not a test result. See [CLXXXVIII in the CI investigation](research/DESCENT_CLXXXVII_ISOLATED_CI_PRE_RUNNER_FAILURE.md). Production remains HOLD.


### CLXXXIX — malformed residual values could pass the cone boundary

Both Control Plane entrypoints were found coercing `GREAT_SCALE_S` with `Number(value || 0) || 0`. This maps supplied `NaN`/empty values to zero and allows `Infinity` through; the cone inequality alone treats positive infinity as compliant. PR #33 now adds a strict finite-value parser, explicit `HOLD_INVALID_RESIDUAL` decisions, diagnostic output, regression tests, and focused-workflow coverage. See [CLXXXIX — non-finite residual input](research/DESCENT_CLXXXIX_NONFINITE_RESIDUAL_FAIL_CLOSED.md).

The code and test wiring are committed, but a clean local checkout was unavailable (GitHub DNS/network resolution failed) and hosted Actions has not yet exposed execution steps. Therefore the regression is added but not yet runtime-verified against the repository. This closes neither the producer/consumer signing-protocol mismatch nor production identity/key/live-endpoint requirements. Production remains HOLD.


CLXXXIX verification update: the isolated Node.js 22 parser regression passed 6/6 tests, and a separate runtime reproduction confirmed the old `Number(value || 0) || 0` expression maps `NaN`/non-numeric input to zero and allows `Infinity` to satisfy the cone inequality. This is isolated helper/model evidence only—not a clean-checkout integration run. The latest hosted workflow still failed without visible steps, so hosted test execution remains unverified.


CLXXXIX refinement: residual parsing and cone classification are now centralized in `lib/residual-input.mjs`; both entrypoints consume the same `gateValue` and explicit hold classification. The isolated six-case Node.js regression passed 6/6 tests, including invalid-input holds and finite-but-cone-violating holds. This remains isolated verification, not a clean checkout or full-suite result.


CLXXXIX exact-head CI follow-up: Control Plane PR #33 head `25be705adf58276c32794a508d6b386179071f41` produced Evidence Contract Tests run `40442710744` and Plane CI run `40442710850`; both failed with no visible steps or job logs. This still does not show test failure or success. The isolated six-case parser regression passed locally, while clean-checkout/full-suite and hosted execution remain unverified.
