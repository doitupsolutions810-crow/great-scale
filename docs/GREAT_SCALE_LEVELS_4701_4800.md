# Great Scale Levels 4701–4800 — Assurance must include every verifier and every test entry point

## Descent finding

Hardening the primary proof kernel did not harden the separate truth-table entailment checker. Inspection of `test_truth_table_kernel.js` found recursive AST validation without a shared node/depth budget, recursive evaluation without a global work budget, and ordinary property lookup for Boolean assignments. A second checker that is less bounded can become the weakest point in the assurance pipeline.

A second integration gap was also found: `test_truth_table_kernel.js` was not included in the `npm test` script. Its checks could exist in the repository while required CI silently skipped them.

## Mitigation implemented on the draft PR branch

- Added a recursion depth limit of 256 and one aggregate AST node budget of 10,000 across all assumptions and the conclusion.
- Added a global semantic evaluation work budget of 2,000,000 visited nodes across the complete truth-table run.
- Enforced own-property Boolean valuations; inherited properties and non-Boolean assignments fail closed.
- Added adversarial regression tests for cyclic ASTs, shared aggregate node limits, repeated truth-table work, malformed valuation semantics, inherited/extra AST fields, sparse assumptions, oversized assumption arrays, and accessor-backed claim fields.
- Required exact data-only schemas for claim and formula AST objects; reject inherited fields, unexpected keys, and accessors before evaluation.
- Added `node test_truth_table_kernel.js` to the required `npm test` script, so the independent checker suite is included in the intended CI entry point.

The test checker still uses classical propositional semantics over at most 16 variables. Claim envelopes and formula ASTs are restricted to exact own-property, data-only schemas. It is not a theorem prover for arithmetic, higher-order logic, or quantum physics.

## Mathematical model

For a claim (Gammamodelsarphi), the finite truth-table procedure examines every valuation over the atom set (A), with (|A|le16):

[
Gammamodelsarphi iff
orall
uin{0,1}^{A},
left(igwedge_{gammainGamma}llbracketgammarbracket_
uight)
Rightarrowllbracketarphirbracket_
u.
]

To make the implementation a bounded procedure, let (N_{m ast}) be the number of AST nodes across assumptions and conclusion, (D) the maximum nesting depth, and (W) the cumulative number of semantic AST visits over all evaluated valuations. The checker rejects inputs when

[
N_{m ast}>10{,}000,qquad D>256,qquad W>2{,}000{,}000.
]

These are implementation resource guards, not mathematical assumptions about truth. They provide finite operational limits; they do not prove the implementation free of defects.

## Executed reference tests

A targeted equivalent JavaScript harness passed **13/13 checks** after the envelope/schema hardening:
1. valid modus ponens remains accepted;
2. invalid entailment returns a counterexample;
3. cyclic AST is rejected by depth guard;
4. aggregate node budget spans assumptions and conclusion;
5. repeated truth-table work is stopped by global work budget;
6. inherited valuation property is rejected;
7. string-valued assignment is rejected;
8. explicit Boolean false is preserved;
9. unknown operator is rejected;
10. inherited and extra formula fields are rejected;
11. sparse and oversized assumption arrays are rejected;
12. accessor-backed claim fields are rejected without invoking the accessor;
13. 17-variable claims are rejected by the finite truth-table limit.

This harness exercised equivalent logic in the available JavaScript execution environment. It did not execute the repository's actual `npm test` command.

## CI and promotion status

The prior GitHub Actions run still showed `runner_id: 0`, no runner identity, no executed steps, and no logs. The workflow is read-only and time-bounded, but no complete repository test result is verified. The independent checker is now included in `npm test`, increasing the suite's coverage once a real runner executes it.

Do not merge or promote until `npm test` and `python3 test_descent.py` both execute and pass on the exact PR head SHA with real step logs. Keep pull-request code away from privileged self-hosted runners; any runner mitigation must be isolated and minimally privileged.

## Great Scale candidate principle

**Assurance is closed only when every verifier and every verification entry point is inside the same explicit resource, semantic, and execution-evidence contract.** A hardened core surrounded by an unbounded secondary checker—or a regression suite omitted from the CI command—creates an assurance gap even if the core tests pass.

This is a software-assurance result and a candidate systems principle. It does not establish a physical quantum-geometry law.
