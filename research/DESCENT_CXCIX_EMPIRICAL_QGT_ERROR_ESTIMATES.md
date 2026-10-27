# Descent CXCIX — A Richardson difference is not a quadrature certificate

**Status:** Reproduced implementation defect and corrected acceptance contract. This is a numerical-analysis finding for the Qi–Wu–Zhang model, not a new physical law or a claim about experimental data.

## Finding

The earlier Descent XCV called the value `2 * |Q_h - Q_{h/2}| / 3` a rigorous a-posteriori error bound because the band gap is open. That inference is invalid: gap openness ensures smoothness at a fixed gapped mass, but does not supply a numerical upper bound for the unknown global Hessian, nor prove that two sampled grids are already in the asymptotic regime. A Richardson difference is an empirical estimate under additional convergence assumptions, not itself a theorem-backed upper bound.

There was also a separate acceptance defect: `topologicalMappingValid` tested the value labelled “rigorous” against tolerance but did not require the implementation’s own `quadratureConverged` result. A low empirical estimate could therefore authorize a Great Scale scalar even when the direct consecutive-grid/grid-origin checks failed.

## Reproduction before the correction

At Great Scale source commit `f72ed083ebc48e9740ab3e23db81882f95f172da`, call:

```js
qiWuZhangGlobalGeometry(-2.49, 6, 3)
```

The run returns `chernNumber = -1`, `refinedGridSize = 48`, and `quadratureTolerance = 0.001`. Its observed metric-area change is `0.0010147887460911775`, which exceeds tolerance; `quadratureConverged` is `false`. Yet the purported bound is only `0.0006765258307274517`, so the old `topologicalMappingValid` is `true` and `acceptedPsiTopological` is non-null. The added regression was first run against that unchanged implementation and failed on the expected `true !== false` assertion.

A second independent numerical cross-check makes the “bound” misnomer concrete even when the empirical convergence flag is true. At `m=-0.5`, initial grid 12, three refinements, the 48-grid metric-area value is `1.3403251800509002`; its old claimed bound is `0.00004455673261194448`. A direct 2048-grid midpoint sum of the same analytic QGT density is `1.340649355297922`, a difference of `0.000324175247021774`; 1024- and 2048-grid sums differ by about `1.24e-8`. This is strong numerical evidence, not a proof of the exact integral; the proof-level defect is that the code never derives the Hessian bound it claims.

The numerical routines are distinct: `qiWuZhangChernNumber` computes the gauge-invariant FHS plaquette sum, whereas `qiWuZhangLocalIntegrals` samples analytic local QGT curvature and metric density. The historical note’s description of the latter as an FHS plaquette integrand was also imprecise.

## Mathematics and Great Scale mapping

For the gapped two-band pure-state model, the exact local identity used by this bridge is

\[
\sqrt{\det g(k)}=\frac{|F_{12}(k)|}{2}.
\]

For the normalized global budgets

\[
C=\frac{1}{2\pi}\int_{\mathrm{BZ}}F_{12}\,d^2k,\qquad
\mathcal A_Q=\frac{1}{\pi}\int_{\mathrm{BZ}}\sqrt{\det g}\,d^2k
=\frac{1}{2\pi}\int_{\mathrm{BZ}}|F_{12}|\,d^2k,
\]

the triangle inequality gives the true-integral invariant

\[
\mathcal A_Q\ge |C|,\qquad
\mathcal E_Q=\mathcal A_Q-|C|=2\min(P,N),
\]

where \(P=(2\pi)^{-1}\int\max(F_{12},0)\) and \(N=(2\pi)^{-1}\int\max(-F_{12},0)\). The Great Scale channel remains

\[
\tau=\frac{|C|}{\mathcal A_Q},\qquad
S_T=\frac{1-\tau^2}{4},\qquad
\Psi_T=\phi^{-2}+S_T.
\]

The theorem concerns the continuum integral. A finite-grid value and its error indicator are numerical evidence for this mapping, not the theorem itself. `topologicalMappingValid` is therefore an empirical model-level acceptance flag, not a mathematical certificate.

## Mitigation integrated

- Replaced the false “rigorous bound” comments and output names with explicitly empirical Richardson safety-estimate names.
- Added `quadratureConverged` as a required conjunct of `topologicalMappingValid`; an estimate alone can no longer authorize `acceptedPsiTopological` when direct refinement or grid-origin checks fail.
- Preserved the existing FHS integer, Chern-residual, cancellation, entropy, and metric-excess checks. The uncertainty label is explicit as `quadratureErrorEstimateKind: 'empirical-richardson'`.
- Marked Descent XCV as superseded so its former certificate claim cannot be read as the current contract.
- Corrected a separate stale `npm run all` target (`clix` versus the existing `cxlix` candidate-binding test) discovered when running the canonical aggregate; the manifest audit now exercises its registered tests.

## Verification

- Red reproduction on the unmodified source: `node test_topological_qgt.cjs` failed on the new `m=-2.49, grid=6, maxRefinements=3` acceptance regression, as expected.
- Post-fix targeted run: `node test_topological_qgt.cjs` — **24 passed, 0 failed**.
- Post-fix regression: the same counterexample returns `quadratureConverged = false`, `topologicalMappingValid = false`, and `acceptedPsiTopological = null`; a stable `m=-1, grid=40` case remains accepted.
- Full `npm run all` after the manifest repair — **exit 0**, including the test-manifest audit (**27/27**); `git diff --check` — **exit 0**.
- A local pass remains distinct from hosted Actions status and PR enforcement.

## Great Scale placement

- **Micro:** use empirical numerical estimates honestly; do not infer a global derivative bound from two sampled sums.
- **Meso:** keep the discrete topological invariant \(C\) distinct from the quadrature estimate of \(\mathcal A_Q\); fail closed when the configured refinement checks do not converge.
- **Macro:** preserve the exact inequality \(\mathcal A_Q\ge|C|\) and excess identity while treating \(\Psi_T\) as provisional outside the numerical acceptance regime.
- **Meta:** scientific trust requires the evidence type to match its derivation. A finite difference labeled “bound” is not proof; the acceptance state cannot be stronger than the numerical evidence that supports it.

## References in the repository

- [`research/topological-qgt.cjs`](topological-qgt.cjs) — FHS integer, analytic local QGT integration, and empirical refinement logic.
- [`test_topological_qgt.cjs`](../test_topological_qgt.cjs) — phase, identity, and accepted-but-unconverged regression coverage.
- [`DESCENT_XCV_RIGOROUS_BOUND.md`](DESCENT_XCV_RIGOROUS_BOUND.md) — superseded historical claim with an explicit correction notice.
