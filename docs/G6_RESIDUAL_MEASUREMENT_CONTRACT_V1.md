# Great Scale G6 Residual Measurement Contract v1

**Status:** proposed. This contract specifies the numerical evidence that a trusted production-acceptance producer must verify before it signs a G6 residual. It does not claim that Great Scale currently exposes a live production measurement endpoint or that the Control Plane consumes a live signed measurement.

Machine-readable shape: `contracts/g6-residual-measurement/v1.schema.json`.

## Why this exists

The Great Scale residual functions are calculation libraries. A calculated scalar, a default `S=0`, a model output copied into an environment variable, or a signed string saying `S` passed is not by itself an observed production measurement. The production consumer currently accepts a compact residual block only after a separately trusted G0-G6 attestation verifies. The trusted producer must therefore validate the richer underlying measurement before placing its scalar into the compact acceptance artifact.

A critical numerical distinction is now explicit: `research/topological-qgt.cjs` computes Richardson-style estimates (`D/3` with a factor-of-two safety multiplier). Those are empirical/asymptotic error estimates, not rigorous a-posteriori bounds. The code's earlier claim that the estimates bound the unknown maximum Hessian was unsupported by the estimator itself; additionally, the metric-area density includes an absolute value of curvature and is not globally C² across its sign-change set. The model now labels these estimates `richardson-asymptotic-estimate-only` and sets `modelG6CertificationEligible: false`. Its `topologicalMappingValid` result remains a numerical-consistency diagnostic, not production G6 eligibility.

This distinction is material because the topological-QGT model emits more than a scalar: Chern number, integrated and absolute curvature, positive/negative curvature budgets, metric-area budget and excess, signed topological polarization, Great Scale scalar, quadrature errors and tolerances, grid-origin disagreement, and the `topologicalMappingValid` acceptance result. Those diagnostics must not be dropped before G6 acceptance.

## Required bindings

A valid signed receipt binds all of these inputs to the exact model output:

- **Source:** repository identity and a full 40-character commit SHA. The execution's head SHA must equal the source SHA.
- **Execution:** successful workflow run ID and attempt, canonical GitHub Actions run URL, start/completion timestamps, and exact head SHA.
- **Build/artifact:** `measurementBuildId` identifies the Great Scale model/measurement execution and `artifact.digest` identifies its immutable model artifact. Separately, `targetBuildId` and `targetArtifact.digest` identify the intended Control Plane release. All four values are checked against their respective deployment pins; measurement-side and target-side identities must not be collapsed.
- **Model:** fixed model identifier `qi-wu-zhang-two-band`, reviewed model version, explicit mass parameter `m`, base grid size, refinement limit, and an input digest computed from the canonical source/build/model-parameter record.
- **Measurement:** the fields in the schema's `measurement` object, including signed/absolute curvature data, the derived topological tuple, convergence, grid-origin discrepancies, *empirical* Richardson estimates, tolerance, and numerical diagnostic flags.
- **Independent numerical certificate:** a required `numericalCertification` object declaring a reviewed `interval-enclosure-v1` or `analytic-derivative-bound-v1` method, verifier identity, exact model source commit and input digest, certified upper bounds for curvature and metric-area integration error, durable evidence URL and proof digest, a distinct certificate key ID, an Ed25519 certificate signature, and its own generated/expiry timestamps. The signature must verify under a separately deployment-pinned numerical-certificate public key (not the outer G6 receipt key), and the producer must fetch the referenced proof artifact, recompute its digest, and enforce freshness. The `verified` boolean is a claim, not proof by itself.
- **Trust:** canonical payload digest plus Ed25519 signature under an independently provisioned key ID and public key. The payload cannot choose its own trust anchor.

All timestamps must be strict RFC3339/date-time values with sane ordering and bounded freshness. The schema is only a structural envelope; the trusted verifier must independently enforce these cross-field and live-source rules.

## Numerical consistency checks required at verification time

In addition to schema validation, the trusted G6 verifier must check at least:

- `source.commitSha === execution.headSha`, exact run URL ↔ source repository/run ID binding, and a successful run attempt;
- model identifier/version/parameters, `measurementBuildId`, Great Scale source commit and `artifact.digest` match the measurement-side deployment pins; `targetBuildId`, `target.commitSha`, and `targetArtifact.digest` match the target Control Plane release pins;
- `topologicalMappingValid === true` and `quadratureConverged === true` are necessary model diagnostics, but they are not certification; the QGT model's `errorBoundMethod` must identify Richardson values as estimates only, and `modelG6CertificationEligible` is `false` until the independent numerical certificate has been checked;
- `topologicalFloor = abs(chernNumber)`;
- `metricAreaExcess = metricAreaBudget - topologicalFloor` within configured numerical tolerance;
- `signedTopologicalPolarization = sign(chernNumber) × topologicalSaturation`;
- `STopological = (1 - topologicalSaturation²) / 4` and `psiTopological = φ⁻² + STopological`;
- Chern, curvature-cancellation, entropy, grid-origin and quadrature diagnostics satisfy the configured model tolerance;
- `numericalCertification.method` is an approved certificate method; its `certificateKeyId` and Ed25519 `certificateSignature` verify with an independently pinned numerical-certification key; its `generatedAt`/`expiresAt` are ordered and fresh; its `sourceCommitSha` and `modelInputDigest` match the exact source/input; its proof digest matches the fetched durable evidence bytes; and both certified error upper bounds are within `measurement.quadratureTolerance`;
- recomputed canonical input digest, payload digest and Ed25519 signature verify with the independent pinned public key;
- `measuredAt`, `generatedAt` and `expiresAt` are ordered, not future/stale, and all evidence belongs to the same source/build/run.

A model output with missing, non-finite, under-resolved, or failed diagnostics is not eligible for promotion even if its scalar happens to fall in the allowed numeric range. The Richardson estimates are retained for diagnostics but are never substituted for `numericalCertification`.

## Mapping into production G6

Only after the trusted producer verifies this receipt should it translate selected fields into the compact production residual block: `measurement.STopological` → `residual.S`, `measuredAt` → `residual.measuredAt`, the pinned receipt `issuer` → `residual.sourceId`, and `targetBuildId` → `residual.buildId`. The target `target.commitSha` must equal the final Control Plane G0-G6 attestation's `source.commitSha`; `targetArtifact.digest` must equal its `artifact.digest`. The receipt's `source.commitSha` equals its own successful measurement run `execution.headSha`, and `artifact.digest` remains the Great Scale model artifact digest. The consumer `residual.schema` is the compact downstream schema `great-scale.residual-attestation/v1`; the trusted producer validates and maps fields, it does not copy the receipt schema or claim.

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

The focused tests check that the contract names the model's empirical diagnostic fields, that stable/under-resolved QGT outputs are classified correctly, and that a separate numerical certificate is mandatory. The model can report numerical mapping validity without claiming G6 eligibility. The full repository suite and live signed producer/consumer integration still require executable hosted CI, a real interval/analytic certificate producer, and independently provisioned trust anchors.
