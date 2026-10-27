# Descent CLXXV — the source must sign what it says, and contract gates are not production gates

## Finding

The previous descent established that client probe time is not source freshness. A deeper interface audit showed that source-issued timestamps alone still do not authenticate the claims beside them: a producer can timestamp a stale or altered status object unless the timestamp and the exact status payload are cryptographically bound and verified under a separately pinned key.

The connected control plane now expects the complete v5.4.0 status object to include sourceIdentity, sourceKeyId, sourceGeneratedAt, sourceExpiresAt, sourceEvidenceDigest and sourceSignature. The producer in CONTROL12 Lattice Ops PR #31 creates a canonical SHA-256 digest and an Ed25519 signature on each request. The consumer independently pins the public key and key ID; it does not trust the public key merely because the status endpoint supplies it.

## Cryptographic binding

Let \(S\) denote the status object without sourceEvidenceDigest and sourceSignature. Let \(C(S)\) be deterministic canonical JSON with sorted object keys and compact separators. The producer computes:

\[
H = \operatorname{SHA256}(C(S))
\]

It then signs the UTF-8 encoding of the newline-delimited tuple:

\[
M = id \,\|\, "\n" \,\|\, keyId \,\|\, "\n" \,\|\, t_g \,\|\, "\n" \,\|\, t_e \,\|\, "\n" \,\|\, H
\]

\[
\sigma = \operatorname{Ed25519.Sign}(sk, M)
\]

Acceptance requires recomputing H from the received status, matching the expected source identity and separately configured key ID, checking the source timestamps, and successfully verifying \(\sigma\) with the independently pinned public key. The consumer's local checkedAt is not included and cannot refresh the source-issued time.

This binding proves which configured key signed the exact claims, not that a compromised producer tells the truth. The producer key, release process, actual observation source, rotation procedure, and independent event checkpoint remain trust dependencies.

## Contract check namespace is separate from production acceptance

A second interface defect was semantic overloading: using G0–G6 for the status console's own contract-check fields risks making the evidence mechanism appear to assert that production readiness has passed. The new contract uses E0–E6 solely for evidence-console self-checks:

- E0 — source identity
- E1 — signing configuration and private/public key match
- E2 — source timestamp and expiry window
- E3 — exact schema contract
- E4 — payload digest binding
- E5 — signature verification under the pinned key
- E6 — read-only GET behavior

These identifiers are not the production readiness gates G0–G6. Procurement evidence can be structurally trusted while production remains NO_GO. The evidence console must not invent or infer production readiness from its own contract status.

## Time and schema acceptance

The source window remains bounded by a maximum age/lifetime of five minutes and future clock skew of 30 seconds. The producer issues a 60-second expiry on each request and does not store evidence or perform production mutations. Missing signing material or a key-pair mismatch returns HTTP 503 and no authority claim.

The independently checked schema requires all trust fields, binds sourceIdentity and sourceKeyId to expected constants, constrains the digest/signature patterns and timestamp formats, and requires each E0–E6 check exactly once. It must not merge the schema's claim into a missing field in the live status payload.

## Integrated mitigation and local test evidence

CONTROL12 Lattice Ops PR #31 contains a read-only Vercel function scaffold at the project root directory evidence-console/ and wires its tests into the repository preflight workflow. The local isolated Node harness used an ephemeral in-memory Ed25519 keypair and passed 8/8 tests for signed status generation, digest mutation, strict timestamp parsing, expiry, signing configuration, key-pair mismatch, schema rules and GET-only behavior. This is a locally executed harness of the producer source logic—not the full repository suite, a hosted CI result, or a live endpoint check.

The new Great Scale CLXXV model has eight acceptance cases and is wired into the canonical npm run all command. It checks the digest, pinned identity/key ID, freshness, schema field requirements, E/G namespace separation, and fail-closed classification. Its signature-valid input is modeled as an externally observed predicate; cryptographic Ed25519 signing/verification is covered by the separate Node producer tests.

## Deployment and residual boundaries

The new evidence-console scaffold has not been deployed. The existing Vercel project must be owner-verified, configured with Root Directory evidence-console, and given an owner-approved Ed25519 keypair in protected runtime variables. The consumer must independently pin the matching public key and key ID. No production key was generated, and no production deployment was performed. Until the public alias emits v5.4.0 status/schema documents and passes a live, signed verification, procurement remains HOLD_EVIDENCE_CONTROL and production remains NO_GO.

The full assurance rule remains conjunctive:

\[
Accept(R,P,t) = Policy(P)\land Complete(E)\land Authentic(E)\land Fresh(E,t)
\land Reach(T,C)\land Execute(T,R)\land Bound(R)\land Pass(R)
\]

Freshness and signatures still do not prove event completeness. Capability Authority requires recovery testing after ledger-commit/projection-write failure, and an independent sequence/checkpoint is still needed to detect tail truncation. Hosted GitHub Actions in the connected repositories continue to expose empty step lists and unavailable logs, so full exact-head execution remains unknown rather than passed or failed.
