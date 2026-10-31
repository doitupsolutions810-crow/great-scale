# Great Scale CXXVII — Repeated-Sampling Coverage Diagnostics

## Question
How do auxiliary-sample extrema, a fixed expansion margin, and known domain support compare across repeated samples?

## Design
A finite synthetic population has 240 outcomes: 216 zeros, 18 values equal to 0.25, and 6 values equal to 1. Its exact mean is 0.04375. Each repetition samples 120 observed outcomes and 12 auxiliary outcomes without replacement. The observed outcomes contribute to the finite-population mean bounds; auxiliary outcomes define candidate limits.

Three methods are compared:
1. Auxiliary observed min/max used directly.
2. Those extrema expanded by a fixed margin 0.1, clipped to [0,1].
3. Known support [0,1], guaranteed by the synthetic population construction.

## Results (seed 20261010, 5,000 repetitions)
| Method | Empirical containment rate | Mean interval width |
|---|---:|---:|
| Sample extrema | 0.7376 | 0.193525 |
| Fixed margin 0.1 | 1.0000 | 0.230015 |
| Known support [0,1] | 1.0000 | 0.500000 |

These are Monte Carlo results for one finite synthetic population and seed. The 100% rate for the fixed margin is not a general guarantee. The known-support method covers by construction because all population values lie in [0,1], and observed outcomes are exact. The experiment's coverage rates are not confidence levels for arbitrary data-generating processes.

## Equations
For observed sum S, population size G, and m missing units, candidate limits [L,U] yield:
\[
\left[\frac{S+mL}{G},\frac{S+mU}{G}\right].
\]
Containment is checked against the known synthetic target mean. Width is m(U-L)/G.

## Scientific finding
A method's observed coverage on a simulation is distinct from a formal guarantee. A known valid support gives a guarantee under its assumptions; sample extrema and heuristic margins only give empirical performance evidence unless further calibrated theory supports a coverage claim.
