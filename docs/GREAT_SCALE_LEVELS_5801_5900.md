# Great Scale — Levels 5801–5900: bounded atom discovery

## Finding

The truth-table oracle validated the conclusion and every context formula under a shared input-node budget, then recursively walked the same formulas again to collect atom names. The second walk was structurally bounded indirectly by the successful validation, but it was not charged to the input budget and duplicated traversal work.

This was not evidence of an unbounded traversal or a demonstrated exploit. It was an accounting mismatch: the implementation validated a bounded AST, then repeated a separate recursive operation over it.

## Integration

- Extended the internal formula validator with an optional, internal atom accumulator.
- During the existing validation pass, atom leaves are added to the accumulator.
- `tautologyUnderContext` now validates the conclusion and context under the existing shared node budget while collecting atoms in that same pass.
- Removed the extra recursive atom-collection walk. Atom ordering and truth-table semantics are preserved.
- Added a large-formula regression that exercises atom discovery through the bounded validation path.

## Mathematics

Let (V(F)) denote the nodes visited while validating formulas (F), and (C(F)) the nodes visited while collecting atoms. The previous path performed approximately
[
W_{mathrm{old}}(F)=V(F)+C(F),
]
with the second term outside the explicit input-node counter. The integrated path performs
[
W_{mathrm{new}}(F)=V(F), qquad 	ext{atoms}(F)	ext{ collected during }V(F).
]
The shared validation counter remains bounded by (mathrm{MAX_NODES}). Truth-table evaluation retains its distinct (mathrm{MAX_EVAL_STEPS}) budget because AST node count and semantic evaluation work are different resource measures.

## Science and engineering interpretation

This is a software-verification result about accounting and duplicated computation in a propositional-logic oracle. It is not evidence for a new physical law or empirical confirmation of quantum geometry.

## Evidence status

- Source integration: committed to the research branch.
- Regression: added, but not yet executed in a local runtime.
- GitHub Actions: prior exact-head run failed; job step details and artifacts were unavailable from the run record. A fresh run for the new head is required.
- Build: not verified.
- Promotion: blocked until exact-head tests, logs, and receipt are available; PR #89 remains draft and unmerged.
