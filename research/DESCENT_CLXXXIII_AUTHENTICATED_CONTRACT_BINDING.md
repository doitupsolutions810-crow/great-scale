# Descent CLXXXIII — Authenticated Status Is Not Yet an Authenticated Contract

## Finding

The consumer candidate now has a dedicated Ed25519 source verifier and calls it before granting public evidence authority. The trust anchor comes from consumer-side `EVIDENCE_SOURCE_KEY_ID` and `EVIDENCE_SOURCE_PUBLIC_KEY_PEM`, not from the fetched status/schema response. It checks source identity, key ID, canonical status digest, signature, and schema constraints for the source fields. The consumer tests now construct signed fixtures and include tampered-signature and missing-trust-anchor cases.

The next unconnected seam is schema-to-status binding. The producer signs the status envelope, but the signature message does not include a digest of the schema document. The consumer checks selected schema properties, but the schema document itself is not cryptographically bound to the signed status. Thus source authenticity of the status and integrity/version identity of the schema are distinct properties.

## Formal release predicate

Let E be contract semantics valid, G be independent production gates, K be status signature valid against a pinned key, F freshness valid, R exact revision/artifact binding, O observable exact-head CI, and B schema-to-status binding.

`ReleaseAuthorized = E ∧ G ∧ K ∧ F ∧ R ∧ O ∧ B`

A signature on the status cannot imply B unless the signed payload commits to a canonical schema digest or a separately pinned schema digest is used. A schema endpoint that merely says it requires signatures is not itself proof that a particular status was signed under that schema.

## Candidate code changes

On Control Plane branch `fix/force-procurement-evidence-auth`:
- Added `lib/evidence-source-signature.mjs`.
- Updated `lib/evidence-console.mjs` to reject public authority unless source signature and independently configured key ID/public key verify.
- Updated `test/evidence-console.test.mjs` with an Ed25519 fixture and regressions for tampered signatures and absent trust anchors.
- Existing contract validation runs before signature verification so malformed-contract diagnostics remain specific.
- These are source/patch observations. Full repository tests have not been run in this environment; no hosted CI result was returned for the inspected commit.

## Model test

Added `test_great_scale_clxxxiii_schema_binding.py`. It exhaustively evaluates all 128 states of seven independent release predicates and asserts that only the all-true state authorizes, including denial when schema binding alone is absent. This is a policy model, not proof that the producer currently emits a schema digest.

## Next implementation required

1. Add a canonical schema digest to the producer's signed status payload.
2. Add that digest to the producer schema as a required field with a strict SHA-256 pattern.
3. Make the consumer recompute the digest from the fetched schema and compare it to the signed status field before public authorization.
4. Test schema mutation, status mutation, wrong key, key-ID substitution, stale/future evidence, signature corruption, and schema/status cross-pairing.
5. Keep E0–E6 console self-checks distinct from G0–G6 operational gates; the current producer/consumer runtime and gate namespaces still do not match.
6. Require exact-head, observable CI and live deployment verification before activation.

## Gate status

M: HOLD — canonical dual contract not merged.
R: PARTIAL — candidate signature verifier added; complete integration unverified.
E: HOLD — no passing exact-head full-suite evidence.
P: PARTIAL — signed status verification is now implemented in candidate source; schema binding and live trust anchor remain unverified.
A: HOLD — operational G gates and cross-entry-point behavior remain separate proof obligations.
F: CANDIDATE — freshness checks exist, but live signed evidence is not verified.
C: HOLD — schema binding and independent production-gate evidence remain incomplete.
L: HOLD — producer/consumer runtime and E/G namespace mismatch remains.

Release stays HOLD / NO-GO. No merge, deployment, key provisioning, or procurement activation occurred.
