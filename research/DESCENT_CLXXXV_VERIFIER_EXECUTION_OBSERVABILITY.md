# Descent CLXXXV — Verification Integrity Includes the Verifier and Its Execution Channel

## New finding

The schema-binding patch introduced source-level regressions that were visible only when checking the exact committed files rather than relying on the change descriptions:

1. The producer began emitting `sourceSchemaDigest`, but its exact status-field allowlist initially omitted the field. The producer's own status verifier would therefore reject its generated status.
2. The consumer verifier had duplicated/malformed schema constraint fragments after iterative edits.
3. The consumer test fixture had a malformed signed-message delimiter and the direct verifier regression tests initially lacked their import.
4. Hosted evidence is itself incomplete: a producer Actions run ended in `startup_failure` without a job record; a Great Scale test run failed but log retrieval returned `BlobNotFound`; the Control Plane commit's Vercel status reports a build-rate-limit failure. These are distinct from an observed unit-test assertion failure and do not prove code correctness or incorrectness.

## Corrective source changes

- Updated the producer's exact status-field allowlist to include `sourceSchemaDigest`.
- Replaced the consumer verifier with a single, clean implementation of canonical JSON hashing, schema digest comparison, status digest verification, Ed25519 verification, and required schema-field checks.
- Aligned the consumer signature-message delimiter with the producer's newline-delimited Ed25519 message.
- Repaired the consumer test fixture and added direct verifier tests for mutated schemas and missing trust anchors.
- Re-fetched the latest changed files to verify these corrections are present in the candidate branches.

These are source inspection and patch-presence results. The complete JavaScript suites have not been run in a clean checkout, and the latest hosted evidence does not demonstrate a passing exact-head test run.

## Deeper principle: proof of a proof is not execution

A cryptographically correct verifier is insufficient if its own code does not parse, its test fixtures cannot represent the producer's message, or CI cannot expose the executed steps. Therefore, test observability and live deployment verification are independent release predicates, not administrative details.

Let:
- C = source-contract semantics conform
- K = signature verifies against an independently pinned key
- B = fetched schema matches the signed schema digest
- F = source evidence is fresh
- G = independent production-readiness gates pass
- R = exact revision and artifact are bound
- O = exact-head CI is observable and passing
- V = deployed status/schema pair is verified against the pinned key

`ReleaseAuthorized = C ∧ K ∧ B ∧ F ∧ G ∧ R ∧ O ∧ V`

A failed runner startup, missing logs, or a build-rate-limit status cannot be upgraded to a pass. Unknown execution evidence remains non-authorizing.

## Formal model

`test_great_scale_clxxxv_verifier_execution_observability.py` enumerates all 256 states of the eight predicates. Exactly one state should authorize. Each single-predicate failure must deny. The model also asserts that correct source signature and schema binding cannot compensate for missing production gates, unobservable CI, or unverified live deployment.

This is a policy-model test, not a substitute for running the producer/consumer JavaScript suites.

## Remaining integration blocker

Producer `read-only-dynamic` / E0–E6 source-console semantics still differ from consumer `static` / G0–G6 operational readiness semantics. Keep these contracts separate. Do not map E gates to G gates or treat a signed source status as proof that production acceptance gates passed.

## Gate decision

- Source-level regressions from the last iteration: corrected in candidate branches and re-fetched.
- Full test execution: HOLD.
- Exact-head observable CI: HOLD.
- Live producer/consumer contract: HOLD.
- Production key provisioning, merge, deployment, procurement activation: not performed.

Decision: HOLD / NO-GO until the full release predicate is independently satisfied.
