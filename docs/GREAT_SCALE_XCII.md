# Great Scale XCII — Robust Value of Information Under Model Uncertainty

## Question
Does a proposed measurement remain worth its cost across a declared set of plausible models?

## Formalization
For model m, compute EVSI_m = E_m[max_d E_m[U(d,H)|Y]] - max_d E_m[U(d,H)], then net value V_m = EVSI_m - c_m.

For a finite model set M, define V_robust = min over m in M of V_m. This worst-case criterion is a design choice, not a universal optimum. Recommend MEASURE only if V_robust > 0 (with a small floating-point tolerance); otherwise return NOT_ROBUSTLY_WORTH_MEASURING.

## Interpretation
- If all included models yield positive net value, the measurement passes this declared robustness test.
- If at least one plausible model yields zero or negative net value, it is not robustly justified by this criterion.
- A negative worst case does not prove the measurement is bad in the true world; it reveals sensitivity to the included model set.
- The result says nothing about models omitted from the set.

## Example
A perfect binary measurement yields EVSI = 1 utility unit under two-state, +1/-1 decision utilities. If plausible costs are 0.2 and 0.4, net values are 0.8 and 0.6; worst-case net value is 0.6 and the measurement passes. If a plausible model has cost 1.1, the range becomes [-0.1, 0.8], so the robust recommendation is not to measure without further justification.

## Implementation
The robust_value_of_information.py module evaluates a finite list of models using XCI's expected_value_of_sample_information. Each model provides prior, likelihoods, utilities, and optional cost. Outputs include each model's net value, min/max, and conservative recommendation.

## Assumptions and limits
- Models are finite, declared, and decision-compatible.
- Utility units and costs must be comparable across models.
- Worst-case analysis can be over-conservative if implausible models are included.
- It can be falsely reassuring if important models are omitted.
- No statistical confidence is attached to the model set by this calculation.
- For real deployment, justify the model set and test sensitivity to expanding it.

## Pinned finding
**A decision is robust only relative to the uncertainty set it survives.**

## Test scope
Unit tests cover positive and negative worst-case value, range reporting, empty and malformed model sets, and the zero-boundary decision. They verify code behavior, not completeness or empirical validity of the model set.
