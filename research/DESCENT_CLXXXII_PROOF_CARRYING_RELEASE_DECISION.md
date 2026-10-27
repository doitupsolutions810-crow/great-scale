# Descent CLXXXII — Proof-Carrying Release Decision and CI Observability

## New finding

The next missing connection is not another readiness boolean. It is **proof that each readiness claim was actually evaluated against the exact candidate revision**.

The existing evidence model can express “all gates pass,” but release authorization is still not justified if the test result is missing, uninspectable, belongs to another SHA, or cannot distinguish runner startup failure from an actual test failure. A green-looking aggregate label without traceable execution evidence is not release proof.

This finding has two separate dimensions:

- **Policy correctness:** all independent predicates must be true.
- **Proof observability:** the predicate results must be produced by a completed, inspectable run bound to the reviewed commit.

A workflow failure with no job steps/logs is not proof of a code defect, but it is equally not proof of correctness. The only defensible release decision is HOLD until the execution path is observable.

## Release predicate

Let:
- E = console contract valid
- G = independent operational gates pass
- K = signature verifies against an independently pinned key
- F = source evidence fresh and unexpired
- R = evidence binds to the exact revision and immutable artifact
- O = exact-head verification run completed, its relevant steps/logs are observable, and all required suites passed

Then:

`ReleaseAuthorized = E \land G \land K \land F \land R \land O`

O is not a substitute for any security predicate. It is the proof that the implementation and its other predicates were actually tested.

## Model test

Added `test_great_scale_clxxxii_proof_carrying_release.py`. It exhaustively evaluates all 64 states of six Boolean predicates, asserts exactly one all-true authorization state, and checks that every individual missing predicate denies release. This is a formal model, not repository integration or live verification.

## Source/CI observation

The inspected latest Great Scale Actions run, `40438201635`, concluded failure; its job record exposed a failed `test` job but no step details. Therefore it does not identify whether the cause was a test assertion, setup, dependency installation, runner, or another failure. This lack of evidence prevents a trustworthy root-cause diagnosis.

## Operational mitigation

1. Require the release gate to consume the exact commit SHA and immutable artifact digest as inputs.
2. Persist a machine-readable verification record with workflow/run ID, attempt, head SHA, required suite names, individual outcomes, artifact digest, and attestation verification result.
3. Fail closed when any required suite result is absent, skipped, stale, inaccessible, or from another SHA.
4. Keep runner/setup failure classified separately from source-test failure, while both remain non-authorizing.
5. After CI is observable and passing, verify the live signed status/schema with an independently pinned public key.
6. Keep procurement activation behind the same central authorization function; never treat force flags or local fallback as proof.

## Great Scale gate mapping

M: HOLD — canonical dual-contract remains unresolved.
R: PARTIAL — the formal model is wired into aggregate tests, but the complete repository run is not proven.
E: HOLD — latest hosted run failed and is not diagnostically observable.
P: HOLD — consumer-side signature verification is not wired into the inspected probe.
A: HOLD — candidate authorization policy exists, but cross-entry-point end-to-end proof is missing.
F: CANDIDATE — freshness checks exist in source; live signed evidence is unverified.
C: HOLD — independent console and operational evidence are not yet jointly proven.
L: HOLD — live producer/consumer conformance remains unverified.

Therefore release remains HOLD / NO-GO. This report and model do not authorize a merge, deployment, key provisioning, or procurement activation.
