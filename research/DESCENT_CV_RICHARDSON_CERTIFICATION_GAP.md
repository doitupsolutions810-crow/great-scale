# Descent CV — Richardson differences are not rigorous error bounds without an independent regularity bound

**Research audit only.** This note does not change the numerical engine or assert that any reported Qi–Wu–Zhang topology value is wrong.

## Source inspected

The pinned Great Scale source `research/topological-qgt.cjs` at commit `74cad04cf43746e098b8af50af9c811da6b313a4` computes
`curvatureRichardsonErrorEstimate = abs(I_{h/2}-I_h)/3`, similarly for area, and exports
`rigorousCurvatureErrorBound = 2 * curvatureRichardsonErrorEstimate` and
`rigorousMetricAreaErrorBound = 2 * metricAreaRichardsonErrorEstimate`.
It states that these **bound the true quadrature error whenever the gap is open**. The corresponding research note `DESCENT_XCV_RIGOROUS_BOUND.md` says the unknown Hessian maximum is estimated *a posteriori* by the Richardson difference. The code computes neither a rigorous global derivative bound nor interval enclosure for the target integral.

## Exact smooth counterexample (aliasing)

On the periodic interval `[0,1]`, take the infinitely differentiable function

\[
f(x)=\cos(2\pi\cdot 64x),\qquad \int_0^1 f(x)\,dx=0.
\]

For the composite midpoint rule
\[
M_N(f)=\frac1N\sum_{j=0}^{N-1}f\!\left(\frac{j+1/2}{N}\right),
\]
both `N=16` and `N=32` produce **exactly 1 in exact arithmetic** because all sampled phases are integer multiples of `2π`:

\[
M_{16}(f)=M_{32}(f)=1,\quad
D=|M_{32}-M_{16}|=0,\quad
|M_{32}-\int_0^1 f|=1.
\]

Hence **no bound of the form `K*|M_{2N}-M_N|` with finite `K` is universally rigorous from smoothness alone**. The code's `2D/3` would equal zero while the actual fine-grid error equals one. The same counterexample extends to a two-dimensional separable periodic integral by setting `F(x,y)=f(x)`; thus moving from one to two dimensions does not fix the inference.

A QWZ band gap staying open gives regularity, but **regularity does not determine a numerical maximum Hessian from two sampled grids**. This counterexample does not show the QWZ integrand aliases this way; it shows that the *general stated inference* requires an independent theorem or a verified bound for the model family.

## Reproduction

```bash
node research/test_richardson_certification.cjs
```

The standard-library Node test asserts the true error exceeds the reported `2D/3` estimate. On Node 22.16.0 it produced `M16=1`, `M32=1`, `D=0`, `actual error=1`, and exited successfully.

## Required promotion repair

1. Rename the current values to `estimated*Error` and mark their acceptance as **heuristic** until certified; retain any useful empirical acceptance tests but avoid an unsupported claim of mathematically rigorous topological mapping.
2. For a mathematically certified bound, derive and compute an **independent upper bound** on the relevant integrand's second derivatives for the entire gapped parameter domain and grid region, or use interval arithmetic with adaptive verified enclosure. Bound discrete FHS phase approximation separately from continuous quadrature of the local curvature/metric density.
3. Include the mass-dependent gap bound, grid and refinement version, bound derivation, measured residuals, and independent verification result in the provenance envelope.
4. Add non-asymptotic adversarial quadrature tests and checks near gap closings, large finite mass, and grid alignment; require exact-head full suites before any numerical assurance promotion.
5. Keep numerical validity, signed Chern orientation, source provenance, capability authorization and execution receipts as **separate** gate channels.

**Status:** counterexample verified in an isolated Node script, NOT yet a production engine fix. The current QWZ values and current prior CI claims are not reclassified as failed by this note.
