# Great Scale CXXIX — Held-Out Margin Transfer

## Research question
Does a margin selected on one finite synthetic population retain its empirical containment behavior when the population distribution changes?

## Design
Four fixed finite populations of size 240 are tested independently:
- original: 216 zeros, 18 values of 0.25, 6 values of 1 (mean 0.04375);
- rarer extremes: 234 zeros, 4 values of 0.25, 2 values of 1 (mean 0.0125);
- more midrange: 180 zeros, 48 values of 0.25, 12 values of 1 (mean 0.1);
- shifted high: 168 zeros, 48 values of 0.25, 24 values of 1 (mean 0.15).

Each scenario uses 5,000 seeded repetitions, with 120 observed and 12 auxiliary units sampled without replacement. Margins are 0, 0.025, 0.05, 0.1, 0.2, 0.5, and 1.0. The margin 0.05 is treated as a candidate selected on the original scenario; all other scenarios are transfer checks, not formal held-out guarantees.

## Core formula
\[
I(d)=\left[\frac{S+m\max(0,L_0-d)}{G},
\frac{S+m\min(1,U_0+d)}{G}\right].
\]
Containment is the indicator \(\mathbf{1}\{\mu\in I(d)\}\); reported containment is its average across repetitions. Width is \(W(d)=m[U(d)-L(d)]/G\).

## Independently executed results
Using Python's standard library and seed 20261029, with per-scenario seed offsets:
| Scenario | Exact mean | d=0.05 containment | d=0.05 mean width | d=0.1 containment |
|---|---:|---:|---:|---:|
| Original | 0.04375 | 94.50% | 0.206730 | 100.00% |
| Rarer extremes | 0.01250 | 100.00% | 0.092180 | 100.00% |
| More midrange | 0.10000 | 97.24% | 0.307035 | 99.14% |
| Shifted high | 0.15000 | 98.78% | 0.401735 | 98.78% |

## Finding and caveat
The same margin did not produce the same empirical containment rate across scenarios. Here d=0.05 ranged from 94.50% to 100%. The width also varied materially with population composition. This is evidence of distribution sensitivity in this experiment, not a proof about all populations. Since the synthetic populations and their support [0,1] are known, margin 1.0 recovers the support-based interval; its containment is by construction, while its width is less informative.

Do not interpret empirical containment as nominal confidence coverage. Formal guarantees require explicit sampling assumptions and a method whose theorem supports the claim.

## Great Scale mapping
CXXVII: repeated sampling measures empirical containment.
CXXVIII: margin sweeps reveal the containment-width frontier.
CXXIX: transfer checks show the frontier is scenario-dependent.
Next: separate margin selection from validation rigorously and assess performance on predeclared unseen scenarios.
