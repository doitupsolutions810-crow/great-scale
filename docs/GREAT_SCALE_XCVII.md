# Great Scale XCVII — Sequential Validation, Repeated Tuning, and the Cost of Looking

## Question

When does evaluation data cease to be an untouched final test? When results influence a later model or workflow decision, that test has become part of the selection feedback loop.

## Mathematics

For K independent null tests with per-test false-positive rate a:

    FWER = 1 - (1 - a)^K

For a = 0.05 and K = 20, FWER ≈ 0.6415. Independence is required for this exact expression.

Without requiring independence, the union bound gives:

    P(any false positive) <= sum_i P(false positive_i) <= K * a_i

Thus a_i = alpha/K controls familywise error at or below alpha if every individual test is valid at its assigned level. This is the Bonferroni correction. It does not automatically solve every form of model-selection bias.

## Practical protocol

1. Use training data to fit candidates.
2. Use validation data for model selection; log every candidate, metric, look, and decision.
3. Freeze the candidate and evaluation plan.
4. Evaluate once on a previously untouched final test set.
5. If the final test result influences another model decision, stop calling that set untouched. Acquire a new holdout or use a procedure designed for sequential/adaptive evaluation.

Repeated validation is not inherently misconduct; it is expected during tuning. The protection is a final evaluation separated from those choices, or a justified sequentially valid method.

## Implementation

- `sequential_validation.py`: independent-test familywise risk, Bonferroni per-look level, status labels, and event-log audit.
- `tests/test_sequential_validation.py`: deterministic unit tests.
- `artifacts/xcvii_demo.json`: worked example and assumptions.

## Limitations

The independent-look formula is not valid for arbitrary dependent looks. The event audit can only detect behavior recorded in its input log. Status labels are diagnostics, not certificates that a model generalizes. Statistical validity depends on the test design, data provenance, assumptions, and pre-specified analysis.
