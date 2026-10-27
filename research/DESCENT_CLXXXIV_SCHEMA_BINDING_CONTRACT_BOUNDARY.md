# Descent CLXXXIV — Schema Integrity Is Bound, but the Contract Boundary Still Blocks End-to-End Trust

## Source changes made

### Lattice Ops producer candidate — `fix/evidence-contract-source-binding`
- Added exported `sourceSchemaDigest(schemaDocument)`, SHA-256 over the producer's canonical JSON representation of its schema.
- Added required `sourceSchemaDigest` field to the generated schema with a strict 64-character lowercase hexadecimal pattern.
- The generated status includes the schema digest before calculating its own status digest and Ed25519 signature. The status digest therefore commits to the schema digest, and the signature commits to the status digest.
- Producer self-verification recomputes the expected schema digest and rejects a mismatch.
- Updated producer tests to assert schema/status digest agreement and reject a mutated schema digest.

### Control Plane consumer candidate — `fix/force-procurement-evidence-auth`
- The consumer's source verifier recomputes the canonical digest of the fetched schema and compares it to the signed status's `sourceSchemaDigest`.
- It requires the schema to declare `sourceSchemaDigest` as a required SHA-256 field.
- Consumer tests now sign fixture statuses with a schema digest and include negative cases for schema mutation and missing schema-digest schema constraints.

These are committed candidate-source changes. The files were re-fetched to verify that the new code and tests are present. Full repository execution has not yet been demonstrated.

## Important residual blocker

The producer contract still declares `runtime: read-only-dynamic` and E0–E6 console checks. The consumer's general contract validator expects `runtime: static` and G0–G6. Those are different semantic layers: E checks prove the console can attest its own contract; G checks are production acceptance gates.

The signature verifier is invoked only after the consumer's existing contract validation succeeds. Therefore, against the current producer contract, the consumer rejects the payload before the signature/schema-binding gate. This is fail-closed, but it means the two candidates are not yet interoperable.

Do not fix this by renaming E gates to G gates, or by making the consumer treat E checks as production readiness. The correct fix is to define an explicit console-source contract for the signed producer payload and preserve a separate operational-readiness evidence input for G gates. Public source authenticity must not itself satisfy operational gate authorization.

## Formal release predicate

Let C be console contract conformance, K be signature validity against an independently pinned key, B be schema-to-status binding, F be freshness, G be independent production gates, R be exact revision/artifact binding, and O be observable exact-head CI.

`ReleaseAuthorized = C ∧ K ∧ B ∧ F ∧ G ∧ R ∧ O`

The current state has candidate implementation for K and B, but C interoperability, G evidence, R, O, and live verification remain unproven.

## Test status

Source regression cases were added on both repositories, but no full test-suite execution result was available in this session. The Great Scale formal model below tests the policy invariant only; it does not execute the JavaScript producer or consumer.

## Required next steps

1. Define versioned console-source schema and status contracts independently of production G gates.
2. Add the schema digest to the signed producer payload and keep producer/consumer canonicalization byte-for-byte identical.
3. Test real producer-generated status/schema fixtures against the actual consumer verifier, including mutation, wrong key, key-ID substitution, missing field, expiry, and cross-pairing.
4. Preserve an independent G-gate evidence source; prove no procurement entry point can substitute E-series console checks for G-series operational gates.
5. Run producer and consumer suites in clean checkouts and exact-head CI with visible logs.
6. Verify the deployed status/schema pair using an independently pinned public key and compare the live schema digest to the signed status field.
7. Resolve overlapping PR branches before merging. No production activation until all release predicates pass.

## Gate mapping

M: HOLD — versioned dual contract not yet agreed and integrated.
R: HOLD — exact revision/artifact proof remains unverified.
E: HOLD — no passing exact-head full-suite run demonstrated.
P: PARTIAL — candidate producer signature now binds the schema digest; consumer verification is added but not executed end-to-end.
A: HOLD — E/G semantic separation and all procurement entry points remain to be proven.
F: CANDIDATE — source freshness checks exist; live status remains unverified.
C: PARTIAL — schema/status digest binding is implemented in candidate source, but interoperability is blocked by the contract mismatch.
L: HOLD — producer/consumer conformance and live verification are not proven.

Decision: HOLD / NO-GO. No merge, deployment, production key provisioning, or procurement activation was performed.


## Follow-up verification — regression integrity and execution observability

The consumer candidate test file was inspected again after the contract correction. It contained 136 test declarations but only 20 unique names, with repeated blocks appended to the same file. The candidate suite was deduplicated in commit `5ff2d60848164c095c6275994ce9aceb11d2ebf1`: 20 declarations remain, all 20 names are unique, and the four schema-binding regression cases are retained. This is a source-level check; no test execution is implied.

The updated consumer commit has these observable status facts:
- Snyk security check: success.
- Vercel check: failure, with the target reporting a build-rate-limit/plan limitation.
- No GitHub Actions workflow run was returned for the exact consumer commit.
- Producer workflow attempts remain `startup_failure`.
- Great Scale CI run `40441007768` remains failed; the available connector did not expose actionable step logs.

A clean checkout test run was attempted, but this environment could not resolve `github.com`; therefore JavaScript tests could not be executed locally. This is an environment limitation, not a passing test result.

## Updated release interpretation

Test-file integrity is now improved, but the execution predicate remains false until a reproducible test run and exact-head CI evidence exist. A successful security scan does not compensate for a failed build check or absent test execution.

```
ReleaseAuthorized = C ∧ K ∧ B ∧ F ∧ G ∧ R ∧ O ∧ T ∧ L
```

Where `T` is successful, observable test execution and `L` is live status/schema verification against the independently pinned source key. Every predicate is necessary; none is inferred from another.

Decision remains **HOLD / NO-GO**. No merge, deployment, production key provisioning, or procurement activation occurred.

## Follow-up verification — CLXXXV model execution and branch topology

The CLXXXV verifier/execution-observability model was executed directly with Python during this review:
- Result: PASS.
- Truth-table states: 256.
- Authorizing states: exactly 1, the all-true state.
- Single-predicate denial cases: 8/8.
- Explicit denials for missing production gates, observable CI, and live verification all held.
- Scope limitation: this validates the Boolean policy model only; it does not execute the producer or consumer JavaScript, authenticate a live endpoint, or prove deployed key configuration.

Current GitHub topology was re-queried:
- Control Plane PR #31 remains open and draft, head `5ff2d60848164c095c6275994ce9aceb11d2ebf1`, and GitHub reports `mergeable: false`. Its branch compares as 65 commits ahead and 16 behind `main`; reconcile the branch against its current base and inspect conflicts before any merge attempt.
- Lattice Ops PR #31 remains open and draft; its candidate branch compares as 51 commits ahead and 0 behind `main`, but the latest recorded producer Actions attempts have startup failures without a test job result.
- Great Scale PR #128 remains open and draft. Its branch compares as 211 commits ahead and 8 behind `main`; the latest observed CI run, `40441441210`, concluded failure. A branch-to-branch history this large requires careful conflict and workflow-trigger review rather than a blind merge.

These observations strengthen the distinction between policy correctness and release evidence. A passing finite-state model cannot compensate for failed or absent repository CI, a conflicted candidate branch, unverified production gates, or missing live endpoint verification.

Updated release predicate remains:
`ReleaseAuthorized = C ∧ K ∧ B ∧ F ∧ G ∧ R ∧ O ∧ T ∧ L`

Decision: HOLD / NO-GO. Do not merge, deploy, provision production signing keys, or activate procurement until the current branches are reconciled safely and all independent release predicates are evidenced on the exact candidate revisions.

## Descent CLXXXVI — a verified status label is not contract proof

A deeper inspection of the active Control Plane `main` gate namespace found two fail-open edges in `evaluateProcurementReadiness`:
1. Public evidence was accepted from `status === "ok"` and `authority === "public"` without requiring `trustContractVerified === true`.
2. Local fallback accepted an undefined status when local evidence was opted in. An absent status is not proof that a recognized degraded state was observed.

The first edge is a defense-in-depth gap because the probe should only return public/ok after contract verification; the gate helper nevertheless exposed an authorization boundary that did not encode that invariant itself. The second edge could let a caller that supplied incomplete evidence represent it as an eligible local fallback.

### Mitigation staged

A new Control Plane draft PR, [#34](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/34), changes the gate policy to require both the public contract-verification flag and an explicit recognized local degraded status. It adds five repository self-test assertions for these positive and negative cases.

The corrected predicate is:

`EvidenceAuthorized = (PublicOK ∧ TrustContractVerified) ∨ (LocalAuthority ∧ LocalOptIn ∧ RecognizedDegradedStatus)`

`ProcurementReady = CoreReady ∧ EvidenceAuthorized ∧ ConeCompliant`

The recognized degraded statuses are exactly `not_found`, `unreachable`, `unconfigured`, and `invalid`. Missing/unknown status is excluded.

### Verification

- An isolated exhaustive policy harness evaluated 168 combinations across seven status classes, three authority labels, trust proof, local opt-in, and cone compliance. All invariants passed.
- The CLXXXVI Python model is now added to this branch and the aggregate `npm run all` command.
- The committed JavaScript self-test and complete aggregate have not been run in a clean checkout; hosted CI remains required. The source fix is staged in a draft PR, not merged or deployed.

This is a refinement of the broader Great Scale rule: availability and a label are observations; neither substitutes for proof of authority.

### CLXXXVI execution follow-up

The CLXXXVI model was executed directly against its policy logic: **PASS**, 168/168 finite states evaluated, 10 authorizing states, and every authorizing state satisfied either (a) public status plus explicit contract verification or (b) local authority plus recognized degraded status plus explicit opt-in; all also required cone compliance. Negative cases for missing public proof, missing/unknown local status, absent local opt-in, and cone failure passed.

Hosted results remain blocking:
- Control Plane PR #34 run [40441948369](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40441948369): verification/doctor/test/security job failed; downstream container/security job skipped. The available job response contained no step details or logs.
- Great Scale run [40442005831](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40442005831): test job failed; no step details or logs were exposed.
- Control Plane Snyk check passed; Vercel remains failed due to its external daily build quota. Neither result substitutes for the failed test job.

Thus the mitigation is committed to a review branch and formally modeled, but the JavaScript regression is not yet confirmed by a successful repository run. Keep PR #34 and PR #128 unmerged until failures are diagnosed and the exact reviewed heads pass the required suites.

## Descent CLXXXVII — close the proof-production gap

The CLXXXVI gate correction exposed a necessary integration question: where does `trustContractVerified` come from? Inspection of the actual Control Plane probe showed that the previous `probeEvidenceConsole` implementation treated any HTTP 2xx response as `status: "ok", authority: "public"`. It did not parse the response body or call the existing signed-document verifier. Consequently, the new gate condition would correctly deny all real probe responses because the probe never produced the required proof flag.

This is the deeper systems finding: **a policy predicate is only effective when a trusted component produces its proof, and the consumer can trace that proof to an actual verification operation.** Adding a boolean to a test fixture is not an integration.

### Follow-up mitigation staged

The Control Plane draft PR [#34](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/34) now also updates `lib/evidence-console.mjs`:
- HTTP 2xx is treated as reachability, not authorization.
- The response body must parse as a document and pass `verifyEvidenceStatusDocument`, which checks schema, freshness, exact E0–E6 checks, cone state, digest, signature, configured public key, and key ID.
- Only a successful verifier result emits `status: "ok"`, `authority: "public"`, and `trustContractVerified: true`.
- Malformed or unverified documents return `status: "invalid"`, explicitly set the trust flag false, and do not gain public authority.
- Stubbed self-tests now distinguish an HTTP 200 response with failed contract verification from a verified document.

The verifier remains fail-closed when independently configured public-key material and key ID are missing. No production keys were created or changed.

### Verification state

- The finite-state gate policy was re-executed: 168 states evaluated, 10 authorizing states, and five explicit denial invariants passed.
- The changed probe and self-test files were re-fetched from the PR branch and checked for the expected verifier call and regression assertions.
- The JavaScript suite has not been run in a clean checkout. The earlier hosted Control Plane and Great Scale test jobs failed without exposed step logs; those results do not validate this new commit. A fresh exact-head CI run is still required.

Release remains HOLD / NO-GO until the exact PR head passes the JavaScript suite and the deployed public endpoint is verified with independently approved key configuration.

## Descent CLXXXVIII — the cross-repository schema dialect was not connected

A deeper source-to-consumer comparison found that the producer and the Control Plane's pre-existing local status verifier speak different document dialects:

- Producer (control12-lattice-ops/evidence-console/api/status.js) emits version, sourceIdentity, sourceKeyId, sourceSchemaDigest, sourceEvidenceDigest, sourceSignature, sourceGeneratedAt, sourceExpiresAt, overall, and gates.
- The local verifier in the Control Plane expects schema, generatedAt, expiresAt, residual, contractChecks, digest, keyId, and signature.

These are not field aliases. Treating the producer payload as the local format guarantees rejection; translating fields without verifying the producer's original signature would be worse because it would break the signed-byte/field contract.

The producer README and API routes specify two endpoints: /api/status and /api/v1/evidence/schema. The consumer integration has now been adjusted to fetch both, then use a producer-native verifier that:
1. checks exact status fields, expected source identity/key ID and E0–E6 READY gate set;
2. verifies freshness and expiry;
3. recomputes canonical JSON digests for both the status and the independently fetched schema;
4. verifies the Ed25519 signature over the producer's exact newline-delimited tuple using independently pinned consumer public-key material; and
5. denies public authority if either endpoint or verification fails.

Added test/producer-evidence-contract.test.mjs with five regression cases: valid signed pair, schema tampering, status tampering, stale signed evidence, and missing pinned key configuration. The package test command now invokes this suite before the existing self-test and platform suite.

### Remaining proof gap

GitHub Actions continues to report the Plane CI job as failed, but the connector exposes neither step summaries nor downloadable job logs for these runs. The exact failing command is therefore still unknown. Source re-fetch confirms the latest head contains the verifier, dual-endpoint probe, and tests; this is not equivalent to executing those tests. The producer README also states that its scaffold has not been deployed and its prior production alias returned 404, so live source verification remains unproven.

Release remains HOLD / NO-GO pending actionable exact-head CI evidence, a clean full suite, approved key configuration, and a live response from both producer endpoints.

## Descent CLXXXIX — authority label and fallback reason must agree

The final gate review found one more authorization ambiguity in the exported procurement helper: a recognized degraded status plus explicit local opt-in could authorize fallback even when the same evidence object still claimed authority = public. The probe's normal invalid-document path labels accepted fallback as local, but the exported helper must not rely on callers preserving that consistency.

The helper now requires all three local-fallback facts simultaneously: explicit local opt-in, an enumerated observed degraded status, and authority = local. A regression assertion denies the inconsistent combination status = invalid, authority = public, trustContractVerified = false even with local opt-in. This makes the fallback decision a coherent state rather than a status-only heuristic.

The Control Plane PR head is now 2098bfa1aca0e7e925bfd1b6e58f0ad68b307c5c. Its hosted Plane CI job again reports failure without step summaries or downloadable logs; downstream container validation is skipped. This does not identify the failing command and does not count as a test result for the new assertion. Release remains HOLD / NO-GO.

## Descent CXC — verification failure must never be reclassified as availability fallback

A further end-to-end review found a trust downgrade in the Control Plane probe. With local fallback enabled, a reachable public endpoint whose evidence document or schema failed verification could be returned as `status = invalid, authority = local`. The procurement gate accepted `invalid` as a degraded state, so explicit local opt-in could authorize a fallback after a trust failure rather than only after an availability failure.

This is a semantic distinction, not merely an error-label issue:

- **Availability failure**: an explicitly enumerated missing/unreachable/unconfigured source may permit local authority only when local evidence is opted in.
- **Trust failure**: a reachable endpoint with invalid HTTP status, missing schema, malformed JSON, or failed cryptographic verification must remain non-authorizing; changing its authority label must not make it eligible for local fallback.

### Mitigation staged on Control Plane PR #34

- HTTP responses outside 2xx are no longer relabeled as local authority.
- Schema-endpoint failures and status/schema verification failures retain public authority with `trustContractVerified = false`, ensuring they cannot satisfy either public verification or local fallback predicates.
- The procurement gate no longer treats `invalid` as an eligible local-fallback status, even if a caller supplies `authority = local`.
- Regression assertions cover a reachable but unverified response with local opt-in and an explicitly mislabeled local invalid state.
- Changes are staged on `fix/procurement-gate-evidence-contract-binding`; current exact head at report update: `23bb1ab742fd515649f040f2ac1a5bce3afe4ec6`.

### Verification and release status

Source-level checks confirmed the mitigation and regression assertions are present on the branch. The exact-head Plane CI run `40443645735` has now completed with the main verification job failed and the downstream container job skipped. Its job-log endpoint again returned a missing-blob error, so the failing step and cause remain unknown; this is a failed CI result, not a passing test. A clean local `npm test` attempt could not start because the execution environment could not resolve `github.com` for checkout. Thus the JavaScript suite remains unexecuted in this environment. No clean local execution of the JavaScript suite, live public endpoint verification, production key provisioning, merge, or deployment has been established.

**Release remains HOLD / NO-GO** until the exact-head CI run and full JavaScript/platform suite pass, the public status and schema endpoints are verified against independently approved pinned key material, and production behavior is confirmed. No procurement activation is authorized by this mitigation alone.

## Descent CXCI — probe diagnostics and status/schema binding

The Control Plane probe's notes could say local authority was accepted when the returned authority was public and fallback was disabled. The earlier happy-path self-test also injected a verifier that inspected only the status document; it did not prove that the probe fetched the schema route and passed both documents to verification.

Mitigation staged on Control Plane PR #34: probe notes now distinguish fallback eligibility from authorization; regression assertions cover disabled fallback and trust-failure diagnostics; a new probe-level test checks that the status and `/api/v1/evidence/schema` endpoints are both fetched and that the verifier receives the matching pair. Current Control Plane head: `cad38273c6f2f38651f277a6297feca998122f01`.

Verification remains incomplete. Exact-head CI run `40444030236` failed its main job and skipped downstream container checks. The job-log endpoint returned `BlobNotFound`, and local checkout is blocked by DNS failure resolving `github.com`. Source inspection confirms the assertions are committed, but the JavaScript suite has not been shown to pass. Release remains HOLD / NO-GO pending a successful exact-head suite and live verification using independently pinned production key material.

## Descent CXCII — source-contract attestation was being treated as procurement evidence

The deepest current finding is semantic: the producer's `E0-E6` status is explicitly a self-attestation that the contract endpoint can attest its own identity, key configuration, freshness, schema, digest, signature, and read-only behavior. The producer code explicitly says these checks are **not** production acceptance gates `G0-G6`. Yet the consumer's procurement gate previously treated `status=ok + authority=public + trustContractVerified=true` as sufficient public evidence authorization. This conflated verification that a source contract is authentic with verification that the required production-acceptance evidence exists.

### Mitigation staged

- Split `publicContractOk` from `publicOk` in the procurement gate.
- A verified source contract is now reported as contract-valid but remains on HOLD unless a separate `procurementEvidenceVerified=true` signal exists.
- Added regression assertions that contract-only verification is denied and that the gate explains the missing production-acceptance evidence.
- Added a positive policy-model case for a contract plus separately verified acceptance-evidence signal. The current probe does not emit that signal, so the system intentionally remains fail-closed until the separate acceptance artifact and verifier are implemented and wired.
- Corrected the trust-failure probe note to match the regression assertion and corrected the gate note so invalid evidence cannot be described as procurement-ready.

Control Plane PR #34 source changes are staged on `fix/procurement-gate-evidence-contract-binding`; the latest source changes include commits `3ff6a640`, `437c2411`, `fee33ab3`, `1b5a111d`, and `72c78264`.

### Verification state and release decision

Exact-head CI runs for earlier heads failed the main verification job and skipped downstream container checks; the log endpoint returned `BlobNotFound`, preventing identification of the failing step. The current head must run CI again. The JavaScript suite has not been executed successfully in a clean environment, and no separate production-acceptance artifact or live signed endpoint has been verified. The new gate therefore intentionally blocks procurement on source-contract proof alone.

**HOLD / NO-GO remains mandatory.** The final unconnected dependency is not merely network reachability: it is the missing authenticated production-acceptance evidence object, its verifier, and its connection to the procurement decision. Do not merge, deploy, or enable procurement until this dependency is implemented and tested against the exact PR head.

### Post-mitigation CI recheck (2026-10-27)

Control Plane PR #34 exact head is now `72c7826446223c861bffc39af5afc68cd4f137c7`. The source files were re-fetched and confirm the contract/acceptance split and contract-only regression assertions are present. CI run `40444546090` completed with the main verification job failed and downstream container checks skipped. The job log again returns `BlobNotFound`; no failing step can be identified from the available evidence. Thus this is not a verified passing change. The source producer still does not expose a separately verified production-acceptance evidence artifact in the reviewed status/schema contract, and the consumer probe does not emit `procurementEvidenceVerified`. Procurement therefore remains intentionally held.

## Descent CXCIII — close the fallback bypass and reject caller-asserted proof

A further authorization review found that the prior CXCII mitigation still had two weaknesses: the local availability fallback branch could authorize procurement without production-acceptance evidence, and the placeholder `procurementEvidenceVerified: true` property could be supplied by a caller without a dedicated artifact verifier. A boolean assertion is not cryptographic evidence.

### Mitigation staged on Control Plane PR #34

- Commit `a73d0e27` first made local fallback depend on the separate acceptance-evidence predicate.
- Commit `1470497b` added regression tests against local fallback bypass.
- Deeper review showed the boolean itself was not an adequate proof boundary. Commit `d7eaf358` therefore places the procurement evidence predicate in an explicit fail-closed release-hold state until an authoritative production-acceptance verifier is implemented and wired. Neither public contract verification nor local fallback can pass this predicate today.
- Commit `131884fa` changes regression assertions so a caller-supplied `procurementEvidenceVerified: true` is explicitly rejected on both public and local paths.

This is a deliberate safety interlock, not completion of the acceptance evidence integration. It prevents premature procurement authorization but also means no procurement evidence path can become READY until the missing verifier and artifact are actually implemented.

### Current verification status

Exact Control Plane PR head: `131884fa523e10604d6ff78186c937dddd06463a`. Source re-fetch confirms the hard fail-closed predicate and both forged-boolean regression assertions exist. CI run `40444907092` failed; an attempt to rerun failed jobs reported success from the API, but the subsequent status still showed the run completed with failure. The failure log remains unavailable through the log endpoint (`BlobNotFound`), so the cause is unknown. No test suite pass, live endpoint verification, merge, deployment, or procurement activation is claimed.

### Success criteria to exit HOLD

1. Define the authoritative production-acceptance artifact and its provenance/identity contract.
2. Implement a verifier that cryptographically verifies that artifact against independently pinned trust material and validates freshness, environment, required gate set, and digest/signature binding.
3. Make the procurement gate consume a verifier-produced result from that implementation, not caller-supplied Boolean metadata.
4. Add positive and negative integration tests for valid, missing, forged, stale, tampered, wrong-key, wrong-environment, and incomplete-gate evidence on both public and fallback paths.
5. Obtain a successful exact-head CI run and inspect actionable logs; then perform authorized live verification before any merge/deployment decision.

**Release remains HOLD / NO-GO.** The system is safer because the shortcut is closed, but the final evidence connection is still not implemented.
