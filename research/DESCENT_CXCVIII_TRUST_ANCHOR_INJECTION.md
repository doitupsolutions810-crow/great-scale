# Descent CXCVIII — Trust Anchors Must Not Be Caller-Injectable

Date: 2026-10-27

## Finding

After binding both E- and G-namespace decisions to a signed, fresh, build-bound residual, another API boundary was identified: gate functions accepted `acceptanceVerificationOptions`. That parameter could override the verifier's public key, key ID, build ID, and residual source ID if a caller passed custom values. Even with signature verification implemented correctly, allowing an untrusted caller to supply the verification trust anchors undermines the purpose of pinning them in deployment configuration.

This is an API-level trust-boundary defect. The integration entry point did not pass these options, but the exported gate functions exposed the override surface, so the safe design is to remove it from authorization APIs entirely.

## Mitigation committed

Repository: [living-intermediate-control-plane](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane)

Branch: `fix/procurement-gate-evidence-contract-binding`

- Removed `acceptanceVerificationOptions` from both procurement and production gate function signatures.
- Gate authorization now calls the verifier with only the fixed production environment; public key, key ID, build ID, and residual source ID are loaded from deployment-controlled environment configuration inside the verifier.
- Added a regression assertion that passes a valid test-signed artifact plus caller-supplied verifier options and confirms the gate does not authorize using those options.
- The attestation test suite now has 14 explicit assertions, including signed residual provenance cases and trust-anchor override denial. These assertions are authored; successful execution is not yet confirmed.

Relevant commits:
- Gate API trust-anchor removal: `8143db8edefa13336c7bd8ed904c77c3554ed460`
- Diagnostic contract alignment: `3c711f0390b9ca70562bd33d5364566ee8a8e085`
- Test count correction: `87ec92066fc06a6c295d6b388558f13d2d12fd69`
- Trust-anchor override regression test: `cd7b6b05d4ddc56eb3fbfd044e467e50055d1449`

## Verification state

- PR #34 remains open, draft, and unmerged.
- The latest completed CI run observed before the most recent test-only commit was [40448450165](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40448450165), which failed its main verification job and skipped the downstream container/security job.
- The available job-log endpoint returned 404; the job-steps endpoint was empty. The combined commit status separately reports Vercel failure pointing to a build-rate-limit/plan page and Snyk success. These status checks do not identify the root cause of the main CI job failure.
- A likely test-contract issue was identified by source inspection: a self-test expects the lowercase substring `production-acceptance evidence is absent`, while an earlier diagnostic string began with uppercase `Production-acceptance`. The diagnostic was corrected. This is an inspection-based correction, not a confirmed explanation of the inaccessible CI failure.
- No successful exact-head CI run or local execution of the full test suite is established.

## Release criteria and decision

Release still requires all of the following: exact-head tests and CI pass; authoritative producer emits real G0–G6 acceptance and a signed residual measurement; deployment pins the acceptance public key, key ID, build ID, and residual source ID; positive and negative live end-to-end tests verify the same build; and the PR receives review before merge.

**HOLD / NO-GO.** No merge, production key mutation, endpoint configuration, or activation was performed. Missing evidence continues to fail closed.
