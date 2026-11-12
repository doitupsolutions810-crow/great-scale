# Great Scale XCVI — Validation Leakage and Evidence Dependence

## Question
Does the evidence used to validate a candidate provide genuinely new information, or does it reuse data, preprocessing, selection rules, or common causes from model construction?

## Screening logic
Let C be construction source identifiers and T validation source identifiers. The recorded overlap is C intersect T. Additional risk flags capture shared data, preprocessing, or selection rules. Any such flag blocks automatic admission and requires review.

No recorded overlap is not proof of independence. Different filenames can point to the same underlying subjects, instrument, environment, labeling policy, or latent cause. Conversely, a shared high-level source does not always invalidate a validation design; the exact dependence structure matters.

## Group diagnostic
For n observations assigned to g distinct source groups, report g/n as a simple diagnostic. This is not a universal effective-sample-size estimator. If within-group dependence is material, treating all n rows as independent can exaggerate evidence. For exchangeable observations with intraclass correlation rho, a familiar approximation is n_eff = n/[1+(n-1)rho], under its assumptions.

## Admission policy
- Incomplete provenance: do not admit.
- Known overlap or shared construction pipeline: pause admission pending dependence review.
- No recorded overlap but no validation flag: validation remains unconfirmed.
- Recorded independent validation and no detected overlap: eligible for domain review, not certified as true.

## Worked example
Six rows from three groups yield group fraction 3/6 = 0.5. This does not prove the statistical effective sample size is three; it signals that row count alone may overstate independent replication.

## Scientific limits
- Source identifiers and flags are user-supplied metadata, not automatically audited.
- A real independence assessment may need lineage, subject IDs, time windows, instruments, preprocessing versions, and causal assumptions.
- A holdout can still leak through repeated tuning or human selection.
- Passing a leakage screen cannot prove model-set completeness or guarantee out-of-domain performance.

## Pinned finding
**Evidence is independent because of how it was generated—not because it was placed in a separate file or labeled “validation.”**
