# Great Scale XCIV — Adversarial Model Discovery

## Aim
Systematically search for plausible alternatives that could invalidate a current decision, without confusing logical possibility with empirical evidence.

## Discovery loop
1. Freeze the current model, decision, assumptions, and evidence provenance.
2. Search residuals, unexplained observations, boundary cases, and known failure modes.
3. Construct alternative models capable of explaining a discrepancy or reversing a decision.
4. Record assumptions, construction rationale, and evidence reference for every candidate.
5. Test candidates on evidence not used to construct them where feasible.
6. Add candidates that survive scrutiny to the model set, then recompute the robust decision.
7. Preserve a versioned record of why candidates were included, rejected, or left unresolved.

## Expansion theorem
For nonempty model sets M subset M' and model scores V(m), define
V(M) = min_{m in M} V(m).
Then V(M') <= V(M), because the minimum over a superset cannot exceed the minimum over its subset.

This theorem guarantees monotonicity of the worst-case score under set expansion. It does not say every newly imagined model is plausible, nor that every relevant alternative has been found.

## Decision-flip test
Current models A=.8 and B=.6 produce worst-case .6 and pass the strict-positive threshold. Add candidate C=-.1: the worst-case becomes -.1, and the disposition changes from ACCEPT to NOT_CERTIFIED. This is decision-relevant, but whether C belongs in the plausible set must be justified independently.

## Candidate evidence states
- INCOMPLETE_CANDIDATE: required record fields are missing.
- HYPOTHETICAL_CANDIDATE_REQUIRES_EVIDENCE: a constructed counterexample is not yet empirically supported.
- EVIDENCE_BACKED_CANDIDATE_REQUIRES_VALIDATION: evidence exists but candidate still needs validation.

## Scientific safeguards
- Do not treat a search process as exhaustive merely because it was systematic.
- Prefer holdout evidence or independent replication to reduce circular confirmation.
- Distinguish falsification of a model from proof of a specific replacement.
- A changed decision means the candidate is consequential; it does not alone establish that the candidate is true.
- Keep the candidate-search procedure and stopping criteria visible to reduce selective reporting.

## Pinned finding
**A robust conclusion earns credibility not only by surviving known models, but by surviving a documented search for alternatives that could overturn it.**
