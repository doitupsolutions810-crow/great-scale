# Great Scale LXXXVII — Adaptive Discovery of Hidden Common Causes

## Profound finding
A model's ability to explain a failure after observing it is weaker evidence than its ability to predict new outcomes under an independently tested intervention. Discovery and validation must be separate stages.

## Candidate model comparison
Let M0 be the existing dependency model and M1 a candidate model adding a proposed hidden dependency. On discovery data D, compare the likelihood ratio

Lambda_D = P(D | M1) / P(D | M0).

With prior model probability pi, posterior probability under the specified Bayesian model is

P(M1 | D) = pi Lambda_D / ((1-pi) + pi Lambda_D).

This calculation depends on the specified likelihoods and prior. It does not establish causation if the candidate models omit alternatives or if likelihood assumptions are poor.

## Validation gate
Freeze the candidate hypothesis and validation criterion before inspecting the holdout data. Evaluate the candidate on independent validation data V, ideally with an intervention or a prospectively stated prediction that distinguishes M1 from M0. The implementation marks a candidate eligible for human review only when the validation data are declared independent and a supplied validation likelihood ratio reaches a predeclared threshold.

The threshold is a policy input, not a universal constant. The code does not automatically alter the production dependency graph. Passing a statistical gate means eligible for review, not proven causal.

## Safeguards
- Keep the original model and each proposed revision versioned; record data, assumptions, reviewer, and decision.
- Do not reuse discovery data as an independent holdout.
- Account for multiple candidate edges and repeated testing; naive likelihood ratios or p-values can overstate evidence after extensive searching.
- Prefer controlled interventions or natural experiments that distinguish shared-cause explanations from coincident independent failures.
- After acceptance, recalculate LXXXVI reliability under the revised graph and preserve results under the old graph for audit.

## Limitations
A dependency edge can be predictive without being causal. Hidden common causes may remain unobserved; model-selection bias, nonstationarity, and selection effects can invalidate nominal likelihoods. A failed validation does not prove no dependency exists; it means the current evidence did not pass the specified gate.

## Integration
`hidden_common_causes.py` computes a Bayesian posterior probability from supplied prior and likelihood ratio and enforces a separate validation gate. Tests are in `tests/test_hidden_common_causes.py`; they must run in the target environment before validation is claimed.
