# Great Scale XCVIII — Sequential Stopping and the Cost of Looking

## Analysis

XCVII showed that repeated independent tests at per-look false-positive rate alpha0 accumulate familywise risk as 1-(1-alpha0)^K. A natural next question is whether evidence can be monitored over time without treating every look as a fresh uncorrected test.

## E-process for a narrow model

For independent Bernoulli observations X_i, compare a simple null p=p0 against a fixed alternative p=p1. The likelihood ratio after n observations is

    E_n = product_i [p1^X_i (1-p1)^(1-X_i) / (p0^X_i (1-p0)^(1-X_i))].

Under the null and the stated independent Bernoulli sampling model, E_n is a nonnegative likelihood-ratio martingale with E_0=1. Ville's inequality implies

    P_0(sup_n E_n >= 1/alpha) <= alpha.

Thus the evidence can be monitored repeatedly using a predeclared threshold without the naive repeated-testing inflation, under these assumptions. This does not make arbitrary metrics, dependent data, or misspecified null models valid e-processes.

## Worked example

Let p0=0.5 and p1=0.8. A success multiplies E by 1.6; a failure multiplies it by 0.4. At alpha=0.05, the threshold is 20. Three consecutive successes give E=1.6^3=4.096, below threshold; eight consecutive successes give E=1.6^8≈42.95, above threshold. These calculations illustrate the specified simple-vs-simple model, not a universal test for model quality.

## Implementation

- `sequential_stopping.py`: log likelihood ratio, e-value, threshold, stopping decision, and event-log audit.
- `tests/test_sequential_stopping.py`: deterministic unit tests.
- `artifacts/xcviii_demo.json`: assumptions and numerical example.

## Limits and safety

The code is a small statistical reference implementation. It is not a production model-validation gate. Boundary null probabilities can create infinite likelihood ratios for outcomes impossible under the null; use care with degenerate hypotheses. For composite nulls, adaptive alternatives, non-Bernoulli metrics, or dependent observations, use a method whose validity is established for that setting. The audit checks recorded logs only.
