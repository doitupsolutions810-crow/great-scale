# Descent CLXXXI — Two-Source Release Proof and Revision-Bound Authorization

## Finding

The remaining integration seam is architectural: the system needs two distinct evidence classes and must bind them to the same release candidate.

1. **Console trust evidence** proves the evidence console's contract, origin, integrity, and freshness. The Lattice Ops producer candidate emits an E-series contract and Ed25519 signature.
2. **Operational release evidence** proves the actual production gates and binds them to the exact source revision and immutable artifact digest.
3. **Consumer authorization** must verify both classes independently and reject missing, stale, mismatched, unsigned, or ambiguous evidence.

The Control Plane PR #31 candidate expects a static G-series contract but does not verify the producer's source signature/digest fields. Simply changing expected IDs to E-series would be incorrect because it would collapse console self-checks into production readiness. Simply changing the producer runtime to static would also fail to implement the intended source signature trust chain.

## Formal rule

Let E be console-contract validity, G be independently sourced production-gate success, K be signature verification against an independently pinned key, F be source freshness, and R be exact revision/artifact binding.

`Authorize = E \land G \land K \land F \land R`

A console-only policy that checks `E ∧ K ∧ F` but omits `G` and `R` is unsound. The local model exhaustively tested all 32 states and found exactly three unsafe counterexamples: production gates fail, or revision/artifact binding fails, while the console, signature, and freshness checks pass. The safe predicate had zero invariant violations.

## Local test result

`test_great_scale_clxxxi_two_source_release_proof.py` ran locally:
- 32/32 truth-table states evaluated.
- 3 unsafe counterexamples found for the deliberately unsafe policy.
- 0 invariant violations for the safe policy.
- Positive all-predicates case and each single-predicate failure case asserted.

This is a formal policy model only; it does not execute repository code or verify a live endpoint.

## Source audit

On the inspected candidate refs:
- Lattice Ops producer emits `sourceIdentity`, `sourceKeyId`, `sourceEvidenceDigest`, `sourceSignature`; uses `read-only-dynamic` and E0–E6.
- Control Plane consumer expects `static` and G0–G6, validates freshness and `trustContractVerified`, but the inspected module has no source signature/digest/key verification.
- The Control Plane authorization module's local-evidence opt-in is explicit, and the inspected authorization module does not use `FORCE_PROCUREMENT` as an authorization predicate. This is positive candidate-source evidence but not end-to-end release proof.
- Great Scale's aggregate manifest now includes the CLXXX model, but the latest hosted run still concludes failure without actionable step details. The full repository suite is not verified.

## Mitigation plan

1. Define a canonical producer contract version and a separate operational-gate evidence contract. Do not alias E and G identifiers.
2. Add consumer-side Ed25519 verification over the producer's canonical signed payload; pin public key/key ID independently, define rotation/revocation, and reject unsigned or unknown-key responses.
3. Validate source-issued generation/expiry bounds and reject future timestamps, expired evidence, redirects, unexpected endpoint identity, and schema mismatch.
4. Obtain operational G-series evidence from an independently defined source; require every required gate to pass.
5. Bind operational evidence to exact Git revision, image digest, SBOM/report digest, and verified attestation. No “latest” or mutable-tag substitution.
6. Centralize procurement authorization and prove every entry point calls it; force flags and local diagnostic fallbacks must not elevate authority.
7. Wire all producer, consumer, authorization, freshness, schema, signature, supply-chain, runtime-manifest, and platform suites into canonical CI. Require observable steps and a passing run whose head SHA equals the reviewed commit.
8. Verify the deployed producer status/schema pair with an independently pinned public key before any production enablement.

## Acceptance criteria

- [ ] Producer/consumer contract version and schema digest agree.
- [ ] Consumer cryptographically verifies source signature, key ID, source identity, and canonical payload digest.
- [ ] E-series console checks cannot substitute for G-series operational gates.
- [ ] Freshness and exact revision/artifact binding pass.
- [ ] All procurement entry points fail closed on any missing/invalid predicate.
- [ ] Full exact-head CI passes with accessible logs.
- [ ] Live producer signature and schema pass verification.
- [ ] Independent review approves production activation.

## Great Scale mapping

- M: HOLD — canonical dual-contract definition not merged.
- R: PARTIAL — test manifest reaches model checks; full candidate execution remains unproven.
- E: FAIL/HOLD — latest observed Great Scale CI run failed with unavailable step detail.
- P: HOLD — producer signature exists in source, but consumer verification and independent key pinning are not established.
- A: HOLD — shared policy exists in candidate code, but complete cross-entry-point integration is not verified.
- F: CANDIDATE — source timestamps are implemented; live behavior is unverified.
- C: HOLD — source-authenticated console evidence and independent operational evidence must both be present.
- L: HOLD — live producer/consumer conformance is unverified.

Therefore `S = M ∧ R ∧ E ∧ P ∧ A ∧ F ∧ C ∧ L` remains unproven. Procurement stays HOLD and production stays NO-GO. No merge, deployment, key provisioning, or production activation was performed.
