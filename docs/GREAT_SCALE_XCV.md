# Great Scale XCV — Evidence-Gated Model Admission and Decision Stability

## Research question
After XCIV discovers an alternative that could overturn a decision, what evidence is needed before it joins the plausible-model set?

## Separate two operations
1. Exploratory stress test: test a fully described candidate even before it is validated. This reveals vulnerabilities but does not label the candidate plausible.
2. Plausible-set admission: requires recorded independent validation, provenance, stated assumptions, and review that the candidate is relevant to the decision domain. The code flags eligibility; a human/review policy must assess evidence quality and domain relevance.

A candidate can be decision-relevant but poorly supported. Conversely, evidence-backed candidates may not change the current decision. These axes must not be conflated.

## Decision stability calculation
For existing model values V(m), current worst case is v=min_m V(m). For candidate c with score V(c), expanded worst case is v'=min(v,V(c)); therefore v' <= v. With threshold tau, disposition is ACCEPT iff the worst case is strictly greater than tau, otherwise NOT_CERTIFIED.

XCIV example: current scores A=.8, B=.6 yield v=.6 and ACCEPT at tau=0. Candidate C=-.1 yields v'=-.1 and NOT_CERTIFIED. This decision flip demonstrates impact, not empirical truth of C.

## Candidate states
- INCOMPLETE: missing model ID, assumptions, construction rationale, or evidence reference.
- PENDING_INDEPENDENT_VALIDATION: can be stress-tested, not yet eligible for plausible-set admission.
- ELIGIBLE_FOR_PLAUSIBLE_SET_ADMISSION: metadata and independent-validation flag are present; admission still depends on validation quality and domain relevance.
- REJECTED_FOR_CURRENT_EVIDENCE: validation currently contradicts candidate; retain audit trail and revisit if evidence changes.

## Scientific limits
- An independent-validation flag is recorded input, not something this module verifies automatically.
- Independent validation can still be biased, underpowered, or drawn from a mismatched domain.
- Absence of a decision flip does not prove a candidate is irrelevant in every future context.
- The method cannot prove model-set completeness or certify real-world truth.
- Thresholds and model scores must be justified by the application; examples here are synthetic.

## Pinned finding
A candidate earns admission through evidence, not through the size of the decision change it causes. Stress-test broadly; claim plausibility selectively and transparently.
