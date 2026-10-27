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

Hosted verification is **not passed**. The workflow run for this exact head (`40439149122`) completed as failure within seconds. GitHub's job endpoint returned no steps and no log URL; earlier runs show the same empty-step behavior. This does not establish whether the test suite itself fails or whether the runner/service failed before executing steps. A clean checkout and executable local test run remain unavailable in this environment. Do not report CI green.

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
