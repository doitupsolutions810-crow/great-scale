# Descent CLXXVII — Provenance Is the Missing Authorization Edge

## Finding

The control-plane consumer currently establishes transport and structural facts: HTTPS endpoint binding, status/schema contract constraints, gate completeness, and source freshness. Those facts do **not** establish producer identity or payload authenticity. A compromised endpoint or intermediary able to serve a structurally valid, fresh-looking status can still claim `overall: READY`.

The Great Scale CLXXV model introduces `sourceIdentity`, `sourceKeyId`, `sourceEvidenceDigest`, and `sourceSignature`, but its contract currently conflicts with the control-plane validator:
- `runtime`: model says `read-only-dynamic`; consumer requires `static`.
- Gate IDs: model's evidence checks use `E0–E6`; consumer status expects `G0–G6`.
- Consumer's `trustContractVerified` currently means structural contract checks, not cryptographic source verification.

These are not cosmetic naming differences. They make producer/consumer authority ambiguous and can lead to either rejecting legitimate evidence or accepting evidence under a weaker interpretation.

## Formal authorization rule

Let T be transport/endpoint checks; C be the agreed versioned contract; F be freshness; D be recomputed digest validity; S be Ed25519 signature validity; K be pinned source/key identity; and G be exact gate coverage/readiness.

Public evidence authorization is:

`A_public = T ∧ C ∧ F ∧ D ∧ S ∧ K ∧ G`

No condition substitutes for another. In particular, `T ∧ C ∧ F ∧ G` does not imply `A_public`.

Production authorization remains separate:

`A_production = A_core ∧ A_supplyChain ∧ A_public ∧ A_cone`

Local fallback is a distinct, explicitly opted-in diagnostic/procurement path; it must never be relabeled as public or production authority. Force flags are not inputs to either authorization predicate.

## Canonical signing protocol requirements

Before integration, producer and consumer must agree on all of the following in one versioned contract:
1. Exact contract version and runtime value.
2. Separate evidence namespace (`E0–E6`) and production namespace (`G0–G6`); no implicit renaming.
3. Canonical JSON algorithm, UTF-8 handling, key ordering, number representation, and treatment of Unicode.
4. Exact signed bytes. Recommended shape: SHA-256 over canonical status with `sourceEvidenceDigest` and `sourceSignature` omitted; Ed25519 signs the resulting 32-byte digest. Both ends must use the identical rule.
5. Pinned `sourceIdentity`, `sourceKeyId`, and public key. No trust-on-first-use and no key fetched from the same untrusted endpoint.
6. Key rotation/revocation procedure and overlap window.
7. Freshness, expiration, clock-skew and replay rules.
8. Strict failure semantics: absent key, unknown key ID, missing signature, malformed digest, digest mismatch, signature failure, schema disagreement, or stale status means `publicEvidenceAuthorized=false`.

Do not claim cryptographic verification based on field presence, a regex, a test-double boolean, HTTPS, or a valid JSON schema.

## Verification matrix

| Case | Expected result |
|---|---|
| Valid pinned key, canonical digest, valid signature, fresh exact contract | Accept public evidence |
| Flip one payload field after signing | Reject digest and/or signature |
| Replace signature only | Reject signature |
| Correct signature from unknown key ID | Reject pinned-key check |
| Change source identity | Reject identity pin |
| Remove signature or digest | Reject |
| Expired/stale/future timestamp | Reject freshness |
| Swap `E` and `G` namespaces | Reject contract |
| Weaken schema constraints | Reject contract |
| HTTP 200 / READY without cryptographic proof | Reject public authority |
| Local fallback explicitly opted in after observed failure | Local only; never public/production |
| Force flag set | No change in authorization result |

## Integration gate

This document is a contract and review record, **not a claim that runtime signature verification has been implemented**. The producer endpoint and its deployed key identity have not yet been established from available repository evidence. Until those are confirmed, keep the public-evidence gate fail-closed and production HOLD. Do not invent or generate a production trust anchor merely to make tests pass.

Completion requires:
- producer emits the agreed signed envelope;
- consumer recomputes digest and verifies Ed25519 with pinned configuration;
- integration tests exercise real signing/verification and every negative case above;
- clean-checkout full test/build passes;
- a successful hosted workflow is observed on the exact candidate commit;
- deployed producer contract and key configuration are verified.