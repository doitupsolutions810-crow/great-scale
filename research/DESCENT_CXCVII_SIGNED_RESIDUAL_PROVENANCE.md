# Descent CXCVII — The Zero-Residual Default Was a False Measurement

Date: 2026-10-27

## New finding

The previous mitigation closed a caller-supplied `supplyChainOk` bypass, but a deeper trust gap remained: `integrate.mjs` derived the Great Scale residual from `Number(process.env.GREAT_SCALE_S || 0) || 0`, and the shared residual policy defaults `S = 0`. The cone predicate is `Psi(S) = phi^{-2} + S >= phi^{-2} - 1e-12`, so a missing measurement is silently transformed into the exact boundary value and appears compliant.

This is a measurement-provenance failure: the equation may be evaluated correctly, but its input has not been observed. It is not evidence that a live topology/residual measurement occurred.

## Mitigation committed to the Control Plane candidate branch

Repository: [living-intermediate-control-plane](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane)

Branch: `fix/procurement-gate-evidence-contract-binding`

Changes:
1. `lib/production-acceptance-attestation.mjs` now requires a `residual` object inside the signed acceptance payload:
   - schema `great-scale.residual-attestation/v1`
   - deployment-pinned `PRODUCTION_ACCEPTANCE_RESIDUAL_SOURCE_ID`
   - residual source ID, measurement timestamp, finite numeric `S`, and exact build ID
   - measurement age/future-clock checks
   - cone compliance evaluated against the measured `S`
   - because residual is inside the signed body, the Ed25519 signature covers it.
2. Both E-namespace procurement and G-namespace production authorization now calculate cone compliance from the verified signed residual, not caller `S` or a default.
3. The combined diagnostic no longer reports default `S=0` as an observation. Without valid evidence it reports `observed: false`, `S: null`, `coneOk: false`, and `provenanceVerified: false`.
4. Expanded focused attestation tests to reject absent, stale, untrusted-source, and out-of-cone residual measurements.
5. Added self-test assertions that absent signed evidence keeps both namespaces held and that the default residual is not represented as measured.

Relevant commits:
- Signed residual verification: `e6cbda99a67dccc9242e951ed3dbfcf944787481`
- Both namespaces use verified measurement: `4f9822ccd8723139df3bf81265d0303d2bb9ea2e`
- Diagnostic provenance reporting: `52c5c2f2ae6e4fc2410f194ee761f30d80565cf8`
- Expanded focused tests: `35e880a4aa579de4a3313a007a574bcfa136608d`
- Combined fail-closed regression tests: `9870a42954a5d0504bd6245a93fbe17f0241eb63`

## Success criteria

```
VerifiedAcceptance =
  ExactSchema ∧ ExactG0toG6 ∧ AllPass
  ∧ PinnedEd25519Key ∧ ExpectedKeyId ∧ ExpectedBuildId
  ∧ ValidDigest ∧ ValidSignature ∧ FreshArtifact ∧ UnexpiredArtifact

VerifiedResidual =
  SignedWithAcceptance ∧ ExactResidualSchema
  ∧ PinnedSourceId ∧ SameBuildId ∧ FreshMeasurement
  ∧ FiniteS ∧ ConeCompliant(S)

ProcurementReady =
  CoreReady ∧ EvidenceAuthorized ∧ VerifiedAcceptance
  ∧ VerifiedResidual ∧ ConeCompliant(S)

ProductionAuthorized =
  CoreReady ∧ VerifiedAcceptance ∧ VerifiedResidual ∧ ConeCompliant(S)
```

No input provenance means no residual authorization. A default or environment-derived number alone is not proof of measurement.

## Verification state

- The candidate head is `9870a42954a5d0504bd6245a93fbe17f0241eb63`.
- GitHub queued Plane CI run [40448226049](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40448226049) for that head. At report creation it had not completed.
- No successful exact-head test run is established.
- The producer that measures real topology/residual and emits this new signed residual object is still not independently confirmed. The new `PRODUCTION_ACCEPTANCE_RESIDUAL_SOURCE_ID` deployment trust setting is not confirmed configured.
- No production endpoint, secret, signing key, merge, or procurement/production activation was changed.

## Release decision

**HOLD / NO-GO.** This patch intentionally makes existing artifacts without signed residual provenance fail closed. Do not enable production until the authoritative producer emits the updated schema, deployment trust anchors are independently verified, and exact-head CI plus live end-to-end negative/positive tests pass.
