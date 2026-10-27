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
