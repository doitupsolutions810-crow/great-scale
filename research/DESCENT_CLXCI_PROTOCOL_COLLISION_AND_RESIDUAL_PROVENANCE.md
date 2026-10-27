# Descent CLXCI — overlapping evidence branches encode incompatible trust contracts

Date: 2026-10-27

## Executive finding

A fresh fetch of Control Plane PRs #31 and #33 confirms the overlap warning is a protocol collision, not merely a merge conflict. Both branches modify `integrate.mjs`, `status/procurement-bridge.mjs`, `lib/evidence-console.mjs`, `package.json`, and shared tests, but they encode different producer/consumer assumptions.

### Contract matrix

| Dimension | PR #31 branch | PR #33 branch | Safe conclusion |
|---|---|---|---|
| Evidence gate IDs | E0–E6 | G0–G6 | Not interchangeable; E gates describe evidence/procurement contract checks, G gates describe production acceptance |
| Runtime declaration | `read-only-dynamic` | `static` | Must match the actual deployed producer; cannot be selected by a merge preference |
| Public status authority | v5.4.0 contract plus source-signature helper | v5.4.0 contract plus pinned-key Ed25519 verification in consumer | Verify one canonical signing protocol end to end, including exact bytes/digest and key identity |
| Procurement authorization | Shared `authorizeProcurement` plus supply-chain report and Cosign attestation | `evaluateGateNamespaces`, explicit `supplyChainOk: false` | PR #33 is safer than bypassing production supply-chain checks, but does not incorporate PR #31's shared procurement supply-chain evidence path |
| Alternate entry point | Uses shared supply-chain runtime and authorization policy | Uses live evidence probe and namespace evaluator | Both need the same residual, evidence, and supply-chain decisions without duplicating or weakening gates |
| CI evidence | Isolated policy harnesses documented; hosted Actions still opaque | Isolated gate/parser harnesses documented; hosted Actions still opaque | Neither branch has an observable exact-head full-suite pass |

## Cross-check against actual PR #33 source

The current `lib/gate-namespaces.mjs` explicitly declares:
- E0–E6: evidence-console contract checks for procurement/public evidence.
- G0–G6: production readiness/acceptance gates.
- `ProcurementReady ≠ ProductionAuthorized`.

However, PR #33's `lib/evidence-console.mjs` currently expects the public status payload's seven IDs to be G0–G6 and expects `runtime: static`. Its `lib/evidence-status-document.mjs` describes the emitted entries as E0–E6 and explicitly says it does not claim G0–G6 production authorization. That is a concrete producer/consumer incompatibility inside the same candidate branch, in addition to the cross-PR collision.

This cannot be fixed by relabelling E0–E6 entries as G0–G6. That would convert procurement contract checks into apparent production acceptance without the underlying production evidence. The safe outcomes are:
1. Keep the current producer explicitly non-production and ensure it cannot satisfy a consumer that demands G0–G6; or
2. Implement a genuine production G0–G6 producer whose checks and identity are independently authoritative, then version and test the exact status/schema/signature contract.

The deployed producer and intended runtime contract have not been independently identified in this pass. Therefore neither option should be guessed into production.

## Residual coordinate: validity is not provenance

The strict parser now rejects malformed/non-finite input and enforces the repository-derived `S∈[0,0.25]` domain. That only establishes syntactic and domain validity. A supplied `GREAT_SCALE_S` value is still environment input, not proof that S was derived from a live topology observation or signed by an authoritative producer. The unset default `S=0` is a documented fallback, not a live topology attestation.

Consequently:
- Keep parser/domain checks as a boundary guard.
- Do not describe `residualInput.valid` as provenance or topology verification.
- Production authorization must remain independently blocked until live topology provenance and the production supply-chain/identity gates are verified.
- Procurement readiness must not be represented as production authorization.

## Verification performed in this continuation

- Re-fetched both open draft PRs and their changed-file lists.
- Confirmed PR #31 is currently reported non-mergeable; PR #33 is reported mergeable. This metadata is not a protocol compatibility proof.
- Compared the PR patches for the shared authorization and evidence-console files.
- Recreated the fetched residual parser and cone predicate in an isolated Node.js 22 harness and ran the seven parser/domain tests plus the cone-predicate characterization test: **8/8 passed**; syntax checks passed. This is isolated-source verification, not a clean checkout or full repository run.
- The latest focused Actions job remains failed with no visible steps or retrievable logs. The combined commit status also reports Vercel failure due to a deployment build-rate limit and Snyk success; neither result substitutes for the required test suite.

## Required reconciliation sequence

1. Declare one versioned public status contract, including gate namespace, runtime model, source timestamps, canonical digest bytes, signature algorithm, source identity, key ID, and key rotation policy.
2. Keep procurement E0–E6 and production G0–G6 semantically distinct. If the production consumer requires G0–G6, the producer must actually evaluate those production gates.
3. Port PR #31's shared supply-chain authorization path into a consolidated branch only after the status-contract collision is resolved; preserve fail-closed Cosign verification, immutable image digest, same-revision binding, freshness, and no-skip checks.
4. Bind the residual coordinate to an authenticated topology observation or explicitly label it diagnostic/operator supplied; never infer provenance from numeric range alone.
5. Run the exact consolidated checkout: syntax checks, `node --test test/evidence-console.test.mjs test/gate-namespaces.test.mjs test/residual-input.test.mjs`, full `npm test`, and negative integration cases.
6. Restore observable hosted CI and verify the exact candidate SHA. Then verify live status/schema/signature against the actual deployed producer.
7. Only after every independent predicate is satisfied may release authorization be reconsidered.

Decision: do not merge PR #31 and #33 unchanged; do not promote E0–E6 to G0–G6; do not enable production. **Production remains HOLD.**


## CLXCI-A — executable non-interchangeability regression added

Added a regression to Control Plane `test/evidence-console.test.mjs` that builds and signs the actual E0–E6 procurement document, submits it to the G0–G6 public production consumer validator, and asserts rejection for runtime mismatch, missing source-issued freshness fields, and absent expected gate structure. This codifies the safe boundary rather than adapting E0–E6 into apparent G0–G6 authority.

Commit: `0bf4ca304682d55681a26b063a0917a4bc4b3f4d` on PR #33's branch. The test has been added to the existing focused workflow's already-covered test path, but it has **not yet executed in hosted CI**. The previous 8/8 isolated parser harness does not include this new cross-contract regression. Full repository tests remain unverified.


## CLXCI-B — signature bytes are incompatible even if field names are adapted

The mismatch also exists at the cryptographic boundary:
- `lib/evidence-status-document.mjs` computes a canonical JSON payload string and signs its UTF-8 bytes with Ed25519.
- `lib/evidence-console.mjs` computes a SHA-256 hex digest and verifies the Ed25519 signature over the decoded 32-byte digest (`Buffer.from(digest, 'hex')`).

Those are different signed messages. Copying or renaming `digest/keyId/signature` into `sourceEvidenceDigest/sourceKeyId/sourceSignature` cannot make the signature valid. A compatible protocol must specify one exact signed byte sequence, canonicalization rules, digest encoding, signature encoding, key identity, and producer key ID, then use the same rules in producer and consumer.

Added a regression to PR #33's `test/evidence-console.test.mjs` that constructs a consumer-shaped status signed using the producer's canonical-JSON-byte convention and asserts the consumer's raw-digest verifier rejects it with `signature_verification_failed`. Commit: `6ec69a286c0674f486026b5c981835203493c04e`. A local Node syntax check passed for the added test fragment; the actual repository test has not executed because hosted Actions still fails before visible steps. Do not treat this as a runtime test pass.


### CLXCI-B isolated cryptographic reproduction

A local Node.js 22 cryptographic reproduction signed a 436-byte canonical JSON payload and then attempted to verify that Ed25519 signature over the 32-byte SHA-256 digest. Verification correctly returned `false`; a signature created over the raw digest verified as `true`. This directly confirms the signed-message mismatch. It is a focused crypto reproduction, not execution of the repository test file or full suite.
