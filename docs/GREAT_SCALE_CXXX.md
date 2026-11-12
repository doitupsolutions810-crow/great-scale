# Great Scale CXXX — Independent Calibration and Validation

## Purpose
Separate margin selection from validation, then measure transfer to five predeclared synthetic populations that do not determine the chosen margin.

## Procedure
Calibration population: 216 zeros, 18 values of 0.25, and 6 values of 1 (mean 0.04375). Test margins 0, 0.025, 0.05, 0.1, 0.2, 0.5, and 1.0. Select the smallest margin with empirical calibration containment at least 95%; if none qualifies, use 1.0. Freeze it before validation.

Validation populations:
- rarer_extremes: 234 zeros, 4 values of 0.25, 2 values of 1 (mean 0.0125)
- more_midrange: 180 zeros, 48 values of 0.25, 12 values of 1 (mean 0.1)
- shifted_high: 168 zeros, 48 values of 0.25, 24 values of 1 (mean 0.15)
- heldout_skewed: 150 zeros, 60 values of 0.1, 25 values of 0.6, 15 values of 1 (mean 0.144)
- heldout_spiky: 230 zeros, 5 values of 0.6, 15 values of 1 (mean 0.072)

Each scenario has 5,000 repetitions; 120 units are observed and 12 separate units provide auxiliary extrema. Validation uses independent deterministic seed streams.

## Mathematics
For population size G, observed sum S, missing count m, and auxiliary extrema [L0,U0]:
\[
L(d)=\max(0,L_0-d),\quad U(d)=\min(1,U_0+d),
\]
\[
I(d)=\left[\frac{S+mL(d)}G,\frac{S+mU(d)}G\right].
\]
Empirical containment is \(\hat C(d)=R^{-1}\sum_r 1\{\mu\in I_r(d)\}\). The reported Monte Carlo standard error describes simulation variability; it is not a confidence interval for the population mean or a coverage guarantee.

## Independently executed results
The calibration run selected d=0.05: empirical containment 95.22%, Monte Carlo SE 0.30%, mean width 0.211090. The margin is frozen at 0.05 for all validation scenarios.

| Validation scenario | Exact mean | Containment at d=0.05 | Monte Carlo SE | Mean width |
|---|---:|---:|---:|---:|
| Rarer extremes | 0.01250 | 100.00% | 0.00% | 0.095080 |
| More midrange | 0.10000 | 97.26% | 0.23% | 0.311145 |
| Shifted high | 0.15000 | 98.94% | 0.14% | 0.401445 |
| Held-out skewed | 0.14400 | 96.78% | 0.25% | 0.402178 |
| Held-out spiky | 0.07200 | 67.14% | 0.66% | 0.321994 |

## Finding and caveat
A margin that crosses the empirical 95% threshold on calibration can fail badly on a held-out scenario: d=0.05 gives 67.14% containment in the spiky population. This is evidence of transfer fragility in the designed experiment, not a universal law. Empirical calibration alone does not produce a formal guarantee.

## Great Scale map
CXXVIII: margin sweeps measure the containment-width frontier.
CXXIX: population composition changes the frontier.
CXXX: freeze the margin, then validate independently and report Monte Carlo uncertainty.
Next: specify a sampling model and investigate whether a formal finite-sample guarantee can be derived; otherwise present only sensitivity bounds.
