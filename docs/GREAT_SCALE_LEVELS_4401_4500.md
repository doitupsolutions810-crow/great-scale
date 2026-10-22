# Great Scale Levels 4401–4500 — Hardened Proof Boundaries

## Finding
The earlier reference checker performed some inference-rule tag checks before validating the complete formula AST. That left a gap between “the rule sees the expected operator tag” and “the object is a well-formed formula in the declared language.” The truth-table oracle also needed explicit bounds on exhaustive enumeration.

## Mitigation implemented on this branch
- Validate formula ASTs recursively before proof-rule use: only non-empty atomic strings or exactly ternary arrays for `and`, `or`, and `imp`.
- Reject unknown operators, malformed arity, object-valued atoms, and extra proof-object fields.
- Bound formula/proof depth at 256, node count at 10,000, and truth-table variables at 16.
- Bind a checked proof to an explicit expected conclusion and expected assumption context with `checkBound`; compare contexts as multisets so duplicate assumptions are not silently dropped.
- Add negative tests for malformed formulas, claim substitution, context substitution, resource limits, and an invalid conclusion that a truth-table oracle must reject.
- Update the active `.github/workflows/blank.yml` workflow to run Node tests and the Python descent test with a timeout and read-only repository permissions.

## Success criteria and current evidence
1. Malformed formula syntax is rejected before inference.
2. Unknown rules/operators and schema smuggling fail closed.
3. Proof and formula recursion/resource limits are enforced.
4. The proof must match the exact requested conclusion and assumptions.
5. Finite truth-table countermodels reject invalid entailments within the bounded propositional language.
6. CI must report executed steps and a final success before the repository suite is labeled CI-verified.

The equivalent 30-case test logic was executed in the available JavaScript execution environment; record its actual outcome in the pull request description. GitHub Actions previously returned a job with runner ID 0 and no steps, so hosted CI availability remains a separate unresolved operational condition. Do not interpret a configured workflow, a successful Vercel deployment, or a reference execution as a successful GitHub Actions test run.

## Formal limits
This is a bounded propositional reference checker, not an independently verified proof assistant. The truth-table oracle and kernel share the same informal formula encoding; therefore they are not fully independent implementations. The checks do not establish general metatheoretic soundness, authenticated provenance, empirical validity, or a physical Quantum Geometry Mathematics law.

## Great Scale candidate principle
**A proof artifact must be well-formed, resource-bounded, and bound to the exact claim and assumptions before its inference steps can be considered.** Verification status must include execution provenance; “configured,” “reference-tested,” and “CI-passed” are distinct states.
