# Descent CLXXXVI — producer/consumer protocol mismatch is a trust boundary

Date: 2026-10-26 (repository timestamps may be UTC and roll into 2026-10-27)

## Finding

A fresh source audit of control-plane PR #33 confirms that the repository has a signed procurement evidence producer, but not a compatible G0–G6 production attestation producer. Treating this as a simple field-mapping problem would erase a real cryptographic and authority boundary.

Observed producer contract in `lib/evidence-status-document.mjs`:
- schema `great-scale.evidence-status/v5.4.0`
- `generatedAt`, `expiresAt`, `contractChecks`, `namespaces`, `digest`, `keyId`, `signature`
- evidence checks are E0–E6 and the verifier returns `productionClaimed: false`
- the Ed25519 signature covers UTF-8 bytes of the canonical JSON payload.

Observed consumer contract in `lib/evidence-console.mjs`:
- status fields include `sourceGeneratedAt`, `sourceExpiresAt`, `gates`, `sourceIdentity`, `sourceKeyId`, `sourceEvidenceDigest`, `sourceSignature`
- it requires exact G0–G6 readiness and independently pinned source identity/key ID/public key
- it hashes canonicalized status with `sourceEvidenceDigest` and `sourceSignature` excluded, then verifies Ed25519 over the 32 digest bytes.

Therefore, the contracts differ in field shape, gate namespace, trust identity, digest/signature message, and stated authority. Matching names or copying E0–E6 values into G0–G6 cannot establish equivalent evidence.

## Formal boundary

Let:
- (P): procurement producer document is internally valid and signed;
- (I): producer identity is independently pinned and verified by the consumer;
- (M): producer and consumer use the same versioned canonicalization/signature protocol;
- (G): all G0–G6 production gates are derived from authoritative checks and pass;
- (F): freshness/expiry checks pass;
- (C): exact schema/contract binding passes;
- (X): exact-revision tests execute and pass in observable CI;
- (L): live endpoint and deployed key binding are independently verified.

The public production claim must require:

`A_{prod} = I \land M \land G \land F \land C \land X \land L`

(P) alone is not a substitute for any of (I,M,G). A valid procurement signature proves integrity/authorship only under its own configured trust model; it does not transform procurement evidence into production authorization.

## Mitigation sequence

1. Keep the current E0–E6 producer in the procurement trust domain.
2. Define a separately versioned G0–G6 production-attestation contract with explicit source identity, key ID, freshness, digest, signature, and gate provenance.
3. Derive every G gate from authoritative checks/receipts; reject caller-supplied booleans and namespace relabeling.
4. Pin the production public key and identity independently in the consumer; test wrong-key, wrong-identity, tampered, expired, missing-gate, and E0–E6 replay cases.
5. Make authoritative evidence persistence/verification failure fatal to production authorization.
6. Require exact-head hosted CI with observable executed test steps and live deployed-contract verification before enabling authority.

## Verification status

- Static source inspection: producer/consumer mismatch confirmed.
- Existing regression test: `E0-E6 procurement evidence producer cannot grant G0-G6 production authority` is present on control-plane PR #33 head `3004707d31b4928c58a6fa3ca8b02981aa9b810a`.
- The committed JavaScript regression has **not** been demonstrated to execute in the repository runtime.
- Exact-head workflow run `40440181670` failed; job metadata exposes no steps/logs. Vercel reports a build-rate-limit failure; Snyk success does not substitute for tests.
- No production producer, live G0–G6 status, or independently pinned deployed key was verified.

Decision: production remains **HOLD**; PR #33 and PR #128 remain drafts. This note records source-grounded findings and a proposed integration sequence, not an implemented production producer or a successful runtime test.
