# Descent CXCVI — Production Authorization Had an Unconnected Boolean Bypass

Date: 2026-10-26

## Finding

A second authorization namespace remained weaker than the procurement namespace. The E-namespace required a separately signed, build-bound G0–G6 production-acceptance attestation, but `evaluateProductionAuthorization` in the Control Plane still computed:

```js
productionAuthorized = coreReady && supplyChainOk && cone.coneCompliant
```

That allowed a caller-provided `supplyChainOk: true` boolean to stand in for the signed G0–G6 proof. The combined gate evaluator passed shared options to both namespaces, so the G namespace was an unconnected authorization path even after the E-namespace mitigation. This is a code-level bypass, not proof that a production deployment exploited it.

## Mitigation committed to the Control Plane draft branch

Repository: [living-intermediate-control-plane](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane)

Branch: `fix/procurement-gate-evidence-contract-binding`

Changes:
- `lib/gate-namespaces.mjs` now passes the production acceptance artifact through the G-namespace verifier too.
- Production authorization now requires `coreReady && productionAcceptanceVerified && cone.coneCompliant`.
- `supplyChainOk` remains observable diagnostic input but no longer authorizes production.
- G-namespace results expose `productionAcceptanceVerified` and verifier diagnostics.
- `test/self-test.mjs` adds regression assertions that `supplyChainOk: true` cannot authorize production without a signed attestation, including when verifier options look permissive but the artifact is absent.

Relevant commits:
- Gate enforcement: `b76f621998ab06a9bb28b4a2171fb93255e98c84`
- Regression assertions: `08e1952f2b2249b10bc1af83bc0c74690e08beca`

## Required invariant

```
ProcurementReady = CoreReady ∧ EvidenceAuthorized ∧ ConeCompliant
ProductionAuthorized = CoreReady ∧ VerifiedG0toG6Attestation ∧ ConeCompliant
VerifiedG0toG6Attestation =
  ExactSchema ∧ ExactGateSet ∧ AllPass ∧ Fresh ∧ Unexpired
  ∧ PinnedEd25519Key ∧ ExpectedKeyId ∧ ExpectedBuildId
  ∧ ValidDigest ∧ ValidSignature
```

A caller-supplied Boolean is not an attestation. E0–E6 source-contract checks are not G0–G6 production acceptance. Procurement readiness does not imply production authorization.

## Verification and limitations

- GitHub confirmed the candidate branch head is `08e1952f2b2249b10bc1af83bc0c74690e08beca`; PR #34 remains open and draft.
- A new Plane CI run was triggered for that exact head: [run 40447433929](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40447433929).
- That run completed with **failure** in “Verify, doctor, test, Trivy FS, Snyk”; the downstream container/security job was skipped. The available job-log endpoint returned BlobNotFound and the job-step response was empty, so the failing command could not be established.
- Snyk reported success; Vercel reported failure due to its build-rate-limit/plan target. Neither is a substitute for a passing repository test job.
- The new regression assertions are committed but are **not confirmed executed successfully**. No live production endpoint, trusted deployment key configuration, authoritative G0–G6 producer, or successful exact-head CI run is verified here.

## Release decision

**HOLD / NO-GO.** The Boolean bypass is closed in candidate source, but do not merge or enable production authorization until the exact head passes the full test suite and CI, the authoritative producer measures real G0–G6 criteria, the pinned trust configuration is independently verified, and live artifact/build binding is demonstrated.

The Great Scale residual expression `Psi(S) = phi^-2 + S` is a repository policy criterion; a default `S = 0` does not establish that a live topology/residual measurement was observed. The production producer must bind any residual claim to provenance, measurement time, and exact build identity.
