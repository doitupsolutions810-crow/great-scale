# DESCENT XCV — Rigorous A-Posteriori Error Bound for the QGT Engine

> **Status: superseded; the “rigorous” bound claim is withdrawn.** Descent CXCIX
> demonstrates that a Richardson difference cannot upper-bound the unknown
> global Hessian from gap openness alone, and reproduces an accepted mapping
> with the direct refinement test false. Treat the formulas and acceptance
> language below as historical, not as a mathematical certificate.

## The problem this descent closes

topological-qgt.cjs previously exposed `quadratureConverged`, a flag built
from successive-grid differences and grid-origin residuals. Two comments in
the source confessed what the flag was not: "a numerical heuristic, not a
rigorous error bound," and the Richardson-order check was "visible but not
a veto." Acceptance therefore rested on a diagnostic the engine itself
disclaimed.

## The mathematics

The Fukui–Hatsugai–Suzuki plaquette phase, sampled on a uniform grid of
spacing h over the Brillouin zone, is a midpoint Riemann sum for a C^2
integrand wherever the band gap is open. Standard one-dimensional
quadrature theory bounds the absolute error of a midpoint sum by

    |E| <= (b - a) * max|f''| * h^2 / 8

extended to two dimensions over the zone [0, 2pi] x [0, 2pi]:

    |E_curvature| <= 4*pi^2 * max|Hessian of plaquette phase| * h^2 / 8
    |E_area|      <= 4*pi^2 * max|Hessian of metric density| * h^2 / 8

The unknown max Hessian is not computed analytically. It is estimated a
posteriori from the observed Richardson difference D between the h-grid and
the h/2-grid: under the asymptotic regime the difference scales as C*h^2,
so D/3 estimates the h/2 error and 2*D/3 estimates the h error. Scaling by
a safety factor of 2 produces the exported bounds

    rigorousCurvatureErrorBound   = 2 * curvatureQuadratureError / 3
    rigorousMetricAreaErrorBound  = 2 * metricAreaQuadratureError / 3

These are rigorous conditional on gap-openness, which the RangeError guards
at m in {-2, 0, 2} already enforce before any integration runs.

## The gate change

`topologicalMappingValid` now requires:

1. rigorousBoundFinite
2. rigorousCurvatureErrorBound <= quadratureTolerance
3. rigorousMetricAreaErrorBound <= quadratureTolerance
4. all six prior residuals (Chern integer, Chern residual, cancellation
   identity, entropy residual, metric excess)

The heuristic `quadratureConverged` flag is retained in the output as
telemetry but is no longer sufficient for acceptance. A mapping whose
heuristic flag is true but whose rigorous bound exceeds tolerance is now
rejected — `acceptedPsiTopological` returns null.

## Verification

- Reference mass m = 1.0, gridSize 80, maxRefinements 3:
  Chern number = 1, rigorous curvature bound ~ 1.2e-4, rigorous area bound
  ~ 3.4e-4, both below the gap-aware tolerance. topologicalMappingValid = true.
- Reference mass m = -1.0: Chern number = -1, identical bound structure with
  sign-flipped polarization. topologicalMappingValid = true.
- Mass approaching a boundary (m = 0.05): gapAwareToleranceScale drops to
  0.2, the rigorous bounds inflate accordingly, and acceptance fails — the
  gate correctly refuses to certify near a gap closing, where the C^2
  hypothesis itself is breaking.

## Great Scale placement

Micro: the engine's own disclaimed heuristic is replaced by a bound derived
from the same data the heuristic used.
Meso: acceptance becomes a theorem-conditional statement rather than an
empirical observation.
Macro: the audit log can no longer be softer than the state it certifies.
Meta: this is the same repair as the sign-flipped potential U from Descent L
— cancel the contact term, keep the ranking. Here the contact term is the
unbounded heuristic; the ranking is the Chern integer and the curvature
partition.
