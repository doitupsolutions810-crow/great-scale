# Great Scale G6 Residual Measurement Contract v1

**Status:** proposed. This contract specifies the numerical evidence that a trusted production-acceptance producer must verify before it signs a G6 residual. It does not claim that Great Scale currently exposes a live production measurement endpoint or that the Control Plane consumes a live signed measurement.

Machine-readable shape: `contracts/g6-residual-measurement/v1.schema.json`.

## Why this exists

The Great Scale residual functions are calculation libraries. A calculated scalar, a default `S=0`, a model output copied into an environment variable, or a signed string saying `S` passed is not by itself an observed production measurement. The production consumer currently accepts a compact residual block only after a separately trusted G0-G6 attestation verifies. The trusted producer must therefore validate the richer underlying measurement before placing its scalar into the compact acceptance artifact.

This distinction is material because the topological-QGT model emits more than a scalar: Chern number, integrated and absolute curvature, positive/negative curvature budgets, metric-area budget and excess, signed topological polarization, Great Scale scalar, quadrature errors and tolerances, grid-origin disagreement, and the `topologicalMappingValid` acceptance result. Those diagnostics must not be dropped before G6 acceptance.

## Required bindings

A valid signed receipt binds all of these inputs to the exact model output:

- **Source:** repository identity and a full 40-character commit SHA. The execution's head SHA must equal the source SHA.
- **Execution:** successful workflow run ID and attempt, canonical GitHub Actions run URL, start/completion timestamps, and exact head SHA.
- **Build/artifact:** immutable build ID and SHA-256 artifact digest, both checked against deployment pins.
- **Model:** fixed model identifier `qi-wu-zhang-two-band`, reviewed model version, explicit mass parameter `m`, base grid size, refinement limit, and an input digest computed from the canonical source/build/model-parameter record.
- **Measurement:** the fields in the schema's `measurement` object, including signed/absolute curvature data, the derived topological tuple, convergence, grid-origin discrepancies, error bounds, tolerance, and acceptance flags.
- **Trust:** canonical payload digest plus Ed25519 signature under an independently provisioned key ID and public key. The payload cannot choose its own trust anchor.

All timestamps must be strict RFC3339/date-time values with sane ordering and bounded freshness. The schema is only a structural envelope; the trusted verifier must independently enforce these cross-field and live-source rules.

## Numerical consistency checks required at verification time

In addition to schema validation, the trusted G6 verifier must check at least:

- `source.commitSha === execution.headSha`, exact run URL ↔ source repository/run ID binding, and a successful run attempt;
- model identifier/version/parameters, build ID, source commit and artifact digest match external deployment pins;
- `topologicalMappingValid === true`, `quadratureConverged === true`, and `rigorousBoundFinite === true`;
- `topologicalFloor = abs(chernNumber)`;
- `metricAreaExcess = metricAreaBudget - topologicalFloor` within configured numerical tolerance;
- `signedTopologicalPolarization = sign(chernNumber) × topologicalSaturation`;
- `STopological = (1 - topologicalSaturation²) / 4` and `psiTopological = φ⁻² + STopological`;
- Chern, curvature-cancellation, entropy, grid-origin, quadrature and rigorous-error-bound criteria satisfy the configured model tolerance;
- recomputed canonical input digest, payload digest and Ed25519 signature verify with the independent pinned public key;
- `measuredAt`, `generatedAt` and `expiresAt` are ordered, not future/stale, and all evidence belongs to the same source/build/run.

A model output with missing, non-finite, under-resolved, or failed diagnostics is not eligible for promotion even if its scalar happens to fall in the allowed numeric range.

## Mapping into production G6

Only after the trusted producer verifies this receipt should it map `measurement.STopological` to the compact production residual scalar `S`. The Control Plane's signed G0-G6 attestation must still bind that scalar to its configured residual source ID, build ID, timestamp, source commit, required workflow attempt and artifact digest.

The evidence receipt is referenced by the successful `residual-measurement` suite's durable evidence URL and digest. The producer must fetch/inspect that exact artifact independently; the current Control Plane verifier checks the signed envelope's consistency but does not itself fetch Actions metadata or validate the truth of the underlying measurement claims.

## Explicit non-goals

- This document does not make an E0-E6 evidence-console signature into production acceptance.
- It does not turn the QWZ research fixture into a universal live production measurement.
- It does not generate or deploy a private signing key.
- It does not mark the Great Scale → Control Plane edge verified.
- It does not lift procurement HOLD or production NO-GO.

## Focused contract regression test

```sh
node --test test_g6_residual_measurement_contract.mjs
```

The focused test checks that the contract names the real model diagnostic fields and that accepted/under-resolved model outputs respect the stated promotion boundary. The full repository suite and live signed producer/consumer integration still require executable hosted CI and independently provisioned trust anchors.
