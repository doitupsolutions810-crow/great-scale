# Descent CLXXX — Evidence-Category Confusion and the Self-Attestation Trap

## Executive finding

The most consequential remaining boundary is not merely a schema mismatch. It is the risk that **evidence about the verifier is treated as evidence about the system being verified**.

The producer in `control12-lattice-ops/evidence-console/lib/contract.mjs` declares a v5.4.0 `read-only-dynamic` contract and checks `E0–E6`. The producer's own documentation/tests distinguish those E checks (the evidence console's identity, key configuration, freshness, schema, digest/signature, and read-only behavior) from operational production gates `G0–G6`.

The Control Plane PR #31 consumer instead expects `runtime: static` and the exact gate identifiers `G0–G6`, all READY. Therefore the current candidates disagree both on wire contract and on the semantics of what a READY status means.

## Why this is deeper than a version mismatch

A signed, fresh, schema-valid producer response can prove that a particular console response was generated under a configured source key and conforms to the console's contract. It does not, by itself, prove that independent production gates passed. Cryptographic authenticity preserves the origin and integrity of a claim; it does not upgrade the claim's meaning.

Unsafe transformation:

`E0–E6 all pass` → `pretend G0–G6 passed` → `production authorized`

Safe transformation:

`E0–E6 all pass` → `console contract trusted` AND independently verified `G0–G6 all pass` → evaluate the release policy.

A compatibility change that merely accepts E IDs where G IDs are expected would hide the mismatch rather than repair it.

## Formal model and test

Let:
- (E) = the evidence console's own contract checks pass.
- (G) = independent operational production gates pass.
- (K) = source signature is valid.
- (F) = source evidence is fresh and unexpired.
- (C) = status/schema contract conforms.

Correct authorization requires:

[
A_{	ext{safe}} = E land G land K land F land C
]

The unsafe substitution omits the independent production-gate predicate:

[
A_{	ext{unsafe}} = E land K land F land C
]

An exhaustive 32-state truth-table model was run. It found one decisive counterexample: (E=K=F=C=1) while (G=0). The unsafe predicate authorizes; the safe predicate denies. All 32 states were checked and the safe predicate had zero invariant violations.

A committed regression model is included at `test_great_scale_clxxx_evidence_category_separation.py` and wired into Great Scale's aggregate `npm run all`.

**Scope limit:** this is a formal model regression, not an execution of either repository's full test suite and not proof of live production behavior. It demonstrates why the authorization rule must preserve distinct E and G predicates.

## Source observations

- Control Plane PR #31 consumer source: `lib/evidence-console.mjs` declares `runtime: static`, expects `G0–G6`, and requires all those entries to be READY.
- Lattice Ops producer source: `evidence-console/lib/contract.mjs` declares `runtime: read-only-dynamic`, `CHECK_IDS = E0–E6`, emits a source digest and Ed25519 signature, and verifies the signed status/schema.
- Producer test: `evidence-console/test/contract.test.mjs` explicitly exercises a signed v5.4.0 status with an E0–E6 contract.
- Control Plane PR #31's root `package.json` test command runs `test/self-test.mjs`, `test/evidence-console.test.mjs`, and platform tests; it does not directly run the authorization/runtime-contract suites present in the alternate PR #29 candidate.

## Mitigation decision

1. Keep the producer's E-series as **console trust/contract checks only**.
2. Give operational readiness its own authenticated, revision-bound evidence source and G-series contract.
3. Do not alias E IDs to G IDs or let a generic `overall: READY` field erase the namespace.
4. Pin the canonical contract version and schema digest at the consumer; reject runtime, ID namespace, signature, freshness, or schema mismatches.
5. Bind operational evidence to the exact source revision and immutable artifact digest, then independently verify supply-chain attestation.
6. Make every procurement entry point call the same authorization function; `FORCE_PROCUREMENT` and availability fallback must never bypass it.
7. Run all required authorization, runtime-contract, producer, consumer, supply-chain, and platform tests in the aggregate CI command; obtain actionable failure logs and a passing exact-commit hosted run.
8. Verify the live producer's signed status and schema using an independently pinned public key before enabling production authorization.

## Great Scale mapping

| Predicate | Assessment | Reason |
|---|---|---|
| M — manifest/contract completeness | HOLD | Consumer and producer define incompatible contract values and gate namespaces. |
| R — execution reachability | PARTIAL | Root test command reaches some suites but omits authorization/runtime-contract suites from the alternate candidate. |
| E — exact-revision execution | FAIL/HOLD | Latest inspected Great Scale CI run failed; step-level cause was unavailable. |
| P — provenance/authenticity | PARTIAL/HOLD | Producer source implements Ed25519 signing; deployed key pinning and live signature verification remain unverified. |
| A — authorization | HOLD | No proof yet that E-series cannot be substituted for G-series at every procurement entry point. |
| F — freshness | CANDIDATE | Source-issued timestamps are implemented in candidate source; live behavior is unverified. |
| C — evidence completeness | HOLD | Producer contract evidence is not equivalent to independent production-gate evidence. |
| L — live contract | HOLD | No successful live producer/consumer conformance check established. |

The release invariant (S=M\land R\land E\land P\land A\land F\land C\land L) is **not established**. Procurement remains HOLD; production remains NO-GO. No merge, deployment, key provisioning, or production activation was performed.
