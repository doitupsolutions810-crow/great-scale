# Great Scale CXXX — Independent Calibration and Validation

## Purpose
Separate margin selection from validation, then measure transfer to five predeclared synthetic populations that do not determine the chosen margin.

## Procedure
Calibration population: 216 zeros, 18 values of 0.25, and 6 values of 1 (mean 0.04375). Test the margins 0, 0.025, 0.05, 0.1, 0.2, 0.5, and 1.0. Select the smallest margin with empirical calibration containment at least 95%; if none qualifies, use 1.0. Freeze it before validation.

Validation populations:
- rarer_extremes: 234 zeros, 4 values of 0.25, 2 values of 1 (mean 0.0125)
- more_midrange: 180 zeros, 48 values of 0.25, 12 values of 1 (mean 0.1)
- shifted_high: 168 zeros, 48 values of 0.25, 24 values of 1 (mean 0.15)
- heldout_skewed: 150 zeros, 60 values of 0.1, 25 values of 0.6, 15 values of 1 (mean 0.144)
- heldout_spiky: 230 zeros, 5 values of 0.6, 15 values of 1 (mean 0.072)

Each scenario has 5,000 repetitions; 120 units are observed and 12 separate units are used for auxiliary extrema. Validation uses separate deterministic random seeds.

## Mathematics
For population size G, observed sum S, missing count m, and auxiliary extrema [L0,U0], define
\[
L(d)=\max(0,L_0-d),\quad U(d)=\min(1,U_0+d),
\]
\[
I(d)=\left[\frac{S+mL(d)}G,\frac{S+mU(d)}G\right].
\]
Empirical containment is \(\hat C(d)=R^{-1}\sum_r 1\{\mu\in I_r(d)\}\). Its Monte Carlo standard error is reported as a descriptive estimate; it is not a confidence interval for the population mean or a proof of coverage.

## Results from independent execution
Seed 20261030 selected d=0.05 on calibration (empirical containment 94.98% in this execution), so the rule's 95% threshold is not met; fallback selects d=1.0. Validation at d=1.0 uses known support [0,1], so containment is guaranteed by construction when all population values truly lie in that support. It also gives a wider, less informative interval.

This is an important result: if the selection threshold is not met, the fallback is transparent and conservative, but the experiment does not establish that a narrow margin transfers. Even if a threshold is met, empirical calibration alone is not a universal coverage guarantee.

## Great Scale map
CXXVIII: margin sweeps measure the coverage-width frontier.
CXXIX: the frontier changes with population composition.
CXXX: freeze calibration before validation and quantify Monte Carlo uncertainty.
Next: replace empirical thresholding with a method supported by a formal guarantee under explicit assumptions, or retain the result as sensitivity analysis only.
