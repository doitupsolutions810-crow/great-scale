# Great Scale XCIII — Model-Set Adequacy and Missing Alternatives

## Question
How can a robust decision be qualified when the set of plausible models may omit important alternatives?

## Two separate obligations
1. **Within-set robustness:** evaluate the decision against every model in the declared set.
2. **Model-set adequacy:** document why the set covers the relevant alternatives for this decision.

A completed checklist is evidence that review steps were performed, not proof that every plausible model was included. The checklist deliberately does not convert process completion into a probability of coverage.

## Omission sensitivity bound
Let v be a lower bound on net value among included models. Suppose the omitted-model probability mass is at most eta, and the omitted models' net value is bounded below by L, with L <= v. Under this explicit mixture assumption, a conservative expected-net-value bound is:

V_lower = (1 - eta) v + eta L.

Example: v=0.6, eta=0.1, L=-1 gives V_lower=0.44. If v=0.2, eta=0.5, L=-1, then V_lower=-0.4 and the decision is not certified by this bound.

This is not a universal guarantee. It depends on a defensible omitted-mass bound and a defensible lower bound on omitted-model value. If no meaningful lower bound exists, the calculation cannot establish positive robust value.

## Checklist fields
- decision_scope_defined
- alternatives_searched
- failure_modes_reviewed
- data_sources_documented
- independent_review_completed

The output is ADEQUACY_NOT_ESTABLISHED if any field is absent or not true. If all are true, output CHECKLIST_COMPLETE_REQUIRES_JUSTIFICATION, not “complete coverage proven.”

## Scientific limits
- A checklist cannot prove absence of unknown alternatives.
- Omission-mass estimates need an independent evidentiary basis.
- Bounds are only valid for the specified mixture interpretation.
- Utility, prior, likelihood, and cost uncertainty may remain after this step.
- Do not present the omission-adjusted bound as a frequentist confidence interval or as a guarantee over arbitrary unknown worlds.

## Pinned finding
**Robustness over a set is not robustness beyond that set. Coverage is an evidentiary obligation, not a mathematical side effect.**
