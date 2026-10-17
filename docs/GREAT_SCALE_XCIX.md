# Great Scale XCIX — Composite Alternatives, Mixture Evidence, and Robust Stopping

## Analysis

XCVIII gave a sequential likelihood-ratio process for a fixed Bernoulli null and one fixed alternative. Real investigations may have several predeclared alternatives. Selecting whichever alternative looks best after observing the data can create another selection effect.

## Fixed mixture

Let the null be a fixed Bernoulli(p0), with 0 < p0 < 1. Before observing data, choose alternatives p1,...,pK and fixed weights w_k >= 0 with sum w_k=1. Define

    E_n = sum_k w_k * P_{p_k}(X_1,...,X_n) / P_{p0}(X_1,...,X_n).

Each likelihood ratio is a nonnegative martingale under the null; a fixed convex combination is also a nonnegative martingale with initial value 1. Ville's inequality therefore gives

    P_0(sup_n E_n >= 1/alpha) <= alpha.

This allows evidence to accumulate for a predeclared family of alternatives without selecting a single alternative post hoc. The weights and alternative family must not be chosen by inspecting the same evaluation outcomes.

## Example

For two alternatives p1=0.8 and p2=0.6, weights (0.5, 0.5), p0=0.5, and two successes:
- LR(p1)=1.6^2=2.56
- LR(p2)=1.2^2=1.44
- mixture E=0.5(2.56)+0.5(1.44)=2.00

At alpha=0.05 the threshold remains 20, so this evidence is inconclusive.

## Boundary of the result

This is a fixed-null, finite-mixture result—not a general solution for composite nulls. It assumes independent Bernoulli observations and a predeclared alternative mixture. For a composite null, dependent observations, adaptive model selection, or arbitrary ML scores, a method with guarantees for that exact setting is required. If an adaptive alternative is selected using prior outcomes, validity requires an appropriate predictable betting/e-process construction, not merely rerunning the fixed-mixture formula.

## Implementation

- `mixture_evidence.py`: stable finite-mixture likelihood-ratio calculation and threshold decision.
- `tests/test_mixture_evidence.py`: unit tests.
- `artifacts/xcix_demo.json`: worked example and assumptions.
