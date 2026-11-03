# DESCENT XCV — Auditing the QGT Error-Bound Claim

**Status (2026-10-27): the earlier “rigorous bound” conclusion in this note is superseded.** The quadrature formulas below motivate numerical error analysis, but the observed Richardson difference by itself does not certify an upper bound on the unknown error. The current model intentionally emits empirical estimates and marks itself ineligible to self-certify production G6.

## The problem this descent examined

The QWZ/topological-QGT engine uses successive-grid differences, grid-origin residuals, and an observed Richardson order to assess numerical consistency. Those checks are valuable diagnostics. They are not automatically rigorous error certificates.

## The mathematical distinction

For a midpoint quadrature rule on an interval of width (b-a), a classical bound has the form

`|E| <= (b - a) * max|f''| * h^2 / 24`

when the regularity and derivative-bound assumptions for that rule are established. In two dimensions, analogous estimates require a justified bound over the relevant derivatives of the integrand/metric density and a correct multidimensional remainder argument.

An observed difference (D) between grid resolutions can support a Richardson estimate under an asymptotic convergence model. Under a second-order assumption, (D/3) is commonly used as an estimate of the finer-grid error. But **the assumption that the observed sequence is already in the asymptotic regime is not itself a bound on the unobserved remainder**. Multiplying that estimate by a safety factor does not turn it into a theorem-certified upper bound.

Therefore the previous inference—

`rigorousErrorBound := 2 * RichardsonEstimate`

—was too strong unless backed by an independent proof of the relevant remainder/derivative bound and its applicability to the exact model inputs.

## Current implementation contract

The current `research/topological-qgt.cjs` deliberately exports:

- `curvatureErrorEstimateWithSafetyFactor`
- `metricAreaErrorEstimateWithSafetyFactor`
- `errorEstimatesFinite`
- `errorBoundMethod = "richardson-asymptotic-estimate-only"`
- `modelG6CertificationEligible = false`

The values are estimates, not certified bounds. `topologicalMappingValid` means that the configured numerical-consistency checks on the observed calculation passed; it is not sufficient proof for production gate G6.

The machine-readable receipt, `contracts/g6-residual-measurement/v1.schema.json`, reflects this distinction. It requires the model-side estimates and a separate `numericalCertification` object with a declared method (`interval-enclosure-v1` or `analytic-derivative-bound-v1`), independent verifier identity, source commit, model-input digest, curvature and metric-area upper bounds, proof digest, and evidence URL. The presence of `verified: true` is still only a claim in signed JSON: a trusted producer must independently validate the certificate artifact and its verifier/trust policy.

## Required evidence before claiming rigorous certification

A valid numerical certificate must establish, for the exact pinned model input and source revision, that the reported upper bounds are mathematically justified. At minimum, the independent verification path must:

1. Bind the certificate to the exact Great Scale commit and canonical model-input digest.
2. Validate the selected method and inspect its proof/artifact, not merely trust a `verified` boolean.
3. Establish finite curvature and metric-area error upper bounds from the applicable interval enclosure or analytic derivative bound.
4. Confirm that both certified upper bounds satisfy the configured tolerance and that topological mapping, convergence, grid-origin, Chern, cancellation, entropy, and domain checks also pass.
5. Bind the receipt to the exact successful workflow run/attempt, immutable Great Scale model artifact, `measuredAt`, expiry, target Control Plane source revision, target build ID, and target artifact digest.
6. Verify the receipt digest and Ed25519 signature under an independently pinned key.

A scalar within `[0, 0.25]`, a finite Richardson estimate, a successful schema check, or a signed assertion of success is not a substitute for this chain.

## Historical numerical examples

Earlier experiments reported, for selected QWZ parameters and grid sizes, values around (10^{-4}) for the Richardson curvature/area estimates. Those are empirical results for those runs. They must not be described as certified upper bounds unless the independent numerical certificate above is actually produced and verified for the exact source and inputs.

## G6 promotion conclusion

The model may report a mathematically consistent candidate scalar. It cannot certify its own error bound. Until a real producer emits a signed, exact-input G6 receipt and an independent trusted consumer verifies the numerical certificate, source/run/artifact pins, freshness, and target-release binding, the Great Scale-to-Control-Plane G6 edge remains `proposed-not-verified` and production remains **HOLD / NO-GO**.
