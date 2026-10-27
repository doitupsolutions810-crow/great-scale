# Descent CLXXVIII — Cross-repository trust boundary and release evidence

Date: 2026-10-26 (repository metadata also contains timestamps after midnight UTC)
Decision: HOLD / production NO-GO

## Finding

The evidence-console producer and consumer now have a stronger source-authentication design, but the trust chain has distinct predicates that must not be collapsed:

1. **Contract integrity:** the status payload's canonical SHA-256 digest matches.
2. **Source authenticity:** an Ed25519 signature verifies against an independently pinned key ID/public key.
3. **Freshness:** source-generated and expiry timestamps satisfy the consumer's bounded freshness policy.
4. **Contract conformance:** the independently fetched schema is exact and includes all required source-attestation fields.
5. **Operational readiness:** the actual production acceptance path independently proves its own G0–G6 gates and procurement prerequisites.
6. **Execution evidence:** the exact reviewed revision has passed the full test/CI path on a real runner.
7. **Release authorization:** trusted supply-chain evidence, including report attestation, revision binding, immutable digest, and scanner results, passes.

A pass at predicates 1–4 does not imply 5–7.

## Source inspection

### Lattice Ops PR #31
https://github.com/doitupsolutions810-crow/control12-lattice-ops/pull/31

Reviewed branch: `fix/evidence-contract-source-binding`, head `7358374f173982caaf475fe11a297477e9dcc570`.

- `evidence-console/api/status.js` and `api/v1/evidence/schema.js` return HTTP 503 with no authority claim if producer contract construction fails.
- `evidence-console/lib/contract.mjs` creates a per-request status document with a source timestamp, short expiry, canonical digest, and Ed25519 signature. It verifies the configured private/public key pair and checks the emitted document/schema before returning.
- The schema and status use E0–E6. The producer README explicitly says these are checks of the console's own identity, key configuration, freshness, schema, digest, signature, and read-only behavior—not production gates G0–G6.
- The producer package declares Node `>=22`; the CI preflight runs the contract tests on Node 22. This is a separate runtime contract from the Control Plane root package.

Interpretation: this is source-authenticated contract evidence, not a production-readiness result. No deployment or production key configuration was verified.

### Control Plane PR #29 and #31
- PR #29: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/29
- PR #31: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/31

Both remain open and draft. Their changed-file sets overlap in `integrate.mjs`, `lib/evidence-authorization.mjs`, `lib/evidence-console.mjs`, and `package.json`. PR #31 additionally carries the shared supply-chain evidence runtime, report attestation, procurement bridge, and live verification command. They must not be independently merged without a diff-based consolidation and regression review.

The current PR #31 head is `e6efc75469a93d033070cdfea40d0559767987c4`. Its root Node engine floor was raised to `>=20` to match the platform package invoked by the root test script. This is a verified manifest alignment, not a diagnosed cause of CI failure.

## Execution evidence

- The latest inspected Plane CI run, [40431500304](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40431500304), failed the verification job and skipped downstream security jobs. The connected GitHub job response exposed no step summaries; previous log retrieval returned `BlobNotFound`.
- Earlier run records and PR notes identify jobs with `runner_id=0` and zero steps, indicating some failures occur before test execution. That is unavailable execution evidence, not a code test failure and not a pass.
- The Vercel check separately reported the account's `api-deployments-free-per-day` quota. This infrastructure failure is not proof of application correctness or incorrectness.
- No clean checkout/full repository `npm test` pass on the exact reviewed Control Plane head was established in this inspection.
- The producer source is not verified live. No production key was generated/configured, and no live signed status/schema response was independently validated.

## Great Scale mapping

Let:

- M = manifest/contract completeness
- R = execution reachability
- E = observed successful execution on the exact revision
- P = revision-bound provenance and source authenticity
- A = correct authorization
- F = freshness
- C = evidence completeness
- L = live producer/consumer contract verified

Then:

`S = M ∧ R ∧ E ∧ P ∧ A ∧ F ∧ C ∧ L`

Current disposition:

- M: improved by explicit contract/schema and runtime declarations.
- P: implementation exists for signed source binding, but the live key pin and live signature verification are unverified.
- F: consumer-side source timestamp checks exist; live freshness is unverified.
- A: fail-closed authorization is implemented in the reviewed branches, but the branches overlap and are not consolidated.
- R, E, C, L: not established for the exact release candidate by available evidence.

Therefore `S` is **not proven**. Procurement remains HOLD and production remains NO-GO.

## Required closure sequence

1. Consolidate the overlapping Control Plane PR #29/#31 changes into one reviewed candidate; prove both procurement entry points call the same authorization policy.
2. Restore/obtain real hosted runner execution or reproduce in a clean checkout on the required Node versions; run the full canonical test command on the exact candidate SHA.
3. Verify the deployed Vercel project and root directory with its owner; configure a newly approved Ed25519 key securely; independently pin only the public key and key ID in the consumer.
4. Execute the live evidence-console gate and record the exact status/schema payloads, timestamps, key ID, digest, signature-verification result, and candidate revision without exposing private material.
5. Verify supply-chain report attestation against the actual trusted workflow identity/issuer, exact revision, freshness, immutable image digest, and successful non-skipped scanners.
6. Enable procurement only after every required predicate passes on the same release candidate.

No merge, deployment, key creation, or procurement activation is authorized by this report.


## Follow-up verification — 2026-10-27T01:22Z

The runtime-manifest inconsistency is now mitigated on both inspected Control Plane candidate branches:

- PR #31 branch `fix/force-procurement-evidence-auth` records the earlier root engine floor change to `>=20`.
- PR #29 branch `fix/procurement-evidence-authorization` now independently declares root Node `>=20`, matching `platform/package.json`, and includes `test/runtime-contract.test.mjs` in the root canonical `npm test` command. That test asserts both engine compatibility and reachability of the platform suite.
- The local isolated runtime-manifest harness passed 2/2 assertions. It does not replace full-suite execution.

Latest exact-head hosted evidence remains unavailable:
- Control Plane PR #29 head `0dc761bc1ccc38f1d8304236311dcfe2a32d6ba0`: [40431955723](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40431955723), zero exposed steps and BlobNotFound logs.
- Great Scale PR #128 head `6574c4c0fa631ab5ceb9cc640e2d11f298cef88a`: [40432088896](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40432088896), zero exposed steps and BlobNotFound logs.
- Lattice Ops PR #31 head `7358374f173982caaf475fe11a297477e9dcc570`: [40432035494](https://github.com/doitupsolutions810-crow/control12-lattice-ops/actions/runs/40432035494), startup failure with no job record.
- Capability Authority PR #12 head `dd8c4e38136d3e3e81891045be0ace216a6c5253`: [40429217283](https://github.com/doitupsolutions810-crow/capability-authority/actions/runs/40429217283), no exposed steps/logs.

Source-level isolated checks performed in this descent: producer contract logic 12/12; signed-evidence Great Scale model 8/8; freshness model 6/6; JavaScript freshness rules 7/7; runtime manifest 2/2. These are bounded local checks and do not make the hosted or live-producer predicates true.

The new signed producer remains undeployed; no production key was generated. Overlapping Control Plane PRs #29 and #31 still require diff-based consolidation before merge. Release acceptance is still **not proven**; procurement remains HOLD and production NO-GO.
