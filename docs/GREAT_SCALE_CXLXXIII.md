# Great Scale CXLXXIII — Reproducible Validation Boundary

## Finding from the prior rung
Representation invariance is a metamorphic property, but the repository's evidence chain is incomplete if CI failures cannot be mapped to a specific failing step and reproduced locally. The inspected CXLXXII model file also contained two consecutive `TERMINAL = object()` assignments. The second assignment shadows the first; imports normally see the second object, so this duplication is a maintenance defect rather than proof that terminal edges are currently misclassified.

## Integration
- Remove the duplicate sentinel declaration so the module exposes exactly one terminal identity.
- Add focused regression tests for terminal-edge equivalence, a real `None` state label, and Boolean-versus-integer observations.
- Preserve the CXLXXII metamorphic property and its scope limits.

## Mathematics
Let (M) be a finite labeled transition model and (Q(M)) its coarsest observation/property-respecting behavioral quotient. The prior rung states:
[
Q(\rho(M)) = \rho(Q(M))
]
for bijective, semantics-preserving renamings (ho).

This rung adds a prerequisite for trustworthy evidence: the implementation and test harness must refer to a single terminal marker (	au), with terminal transitions represented distinctly from every valid encoded state label. In particular, (	exttt{None}) is allowed as a state label and must not be identified with (	au).

## Scientific interpretation
A theorem-like invariant is only as useful as the chain from specification to implementation to repeatable observation. A failing CI summary without step logs is not enough to infer that the new invariant is false; it may reflect an unrelated workflow, dependency, or test failure. Therefore this rung treats reproducibility and fault localization as part of the experimental method, not as mathematical evidence by themselves.

## Validation status
Regression tests are authored but have not been executed in this session. GitHub Actions reported failures for several workflows on the CXLXXII commit, but the job-log endpoint returned a missing-log error and the step endpoint returned no steps. Root cause remains undetermined; do not treat this change as proof that CI is repaired.
