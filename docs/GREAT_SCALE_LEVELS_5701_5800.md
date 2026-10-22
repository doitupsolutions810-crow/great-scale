# Great Scale Levels 5701–5800: Aggregate Work Must Cover Every Pass

**Track:** \`research/kernel-hardening-4401-4500\`  
**Scope:** proof-kernel resource accounting across validation and certificate construction  
**Implementation status:** formula-copy traversals now consume the same proof budget as validation; adversarial regression added; full test execution remains unverified.

## 1. Deeper repository finding

Level 5601–5700 moved resource counters behind public API wrappers. A subsequent review found that this closes caller injection but does not, by itself, guarantee aggregate accounting.

In \`proof_kernel.js\`, the \`assume\`, \`impI\`, \`orIL\`, and \`orIR\` paths validate a formula using the proof's shared node budget and then call \`copyFormula\`. Before this level, those copies used \`copyFormula\`'s default fresh budget. The validator and copy were individually bounded, but their combined traversal cost was not charged to the same budget.

Thus a verifier can own its counters and still undercount its work if internal phases silently start fresh counters.

> **A resource budget must follow the work, not merely the public call.**

## 2. Mathematical formulation

Let an operation perform phases \(P_1,\ldots,P_k\), with each phase consuming \(w_i(x)\) units of the chosen logical-work metric. An aggregate budget \(B\) requires

\[
W(x)=\sum_{i=1}^{k}w_i(x)\le B.
\]

If each phase gets an independent counter, the actual guarantee is only

\[
w_i(x)\le B\quad\text{for every }i,
\]

which does not imply \(W(x)\le B\). With four phases each separately permitted to consume nearly \(B\), the combined work can approach \(4B\).

For the proof kernel, node accounting is a logical bound on traversed proof/formula nodes, not a precise wall-clock or byte-allocation guarantee. It should nevertheless include each relevant validation and copying traversal if it is advertised as one aggregate node budget.

## 3. Integrated change

- The \`assume\` path now calls \`copyFormula(data.formula, 0, budget)\`.
- The \`impI\` path passes the same budget while copying the discharged assumption formula.
- Both \`orIL\` and \`orIR\` pass the same budget while copying their auxiliary formula.
- Recursive \`copyFormula\` calls continue sharing the supplied budget.
- Added a regression test, **\`formula validation and certificate copying share one aggregate budget\`**, which builds a balanced formula whose validation pass fits under the node limit but whose validation plus copy should exceed the shared limit.

The intended behavior is rejection before aggregate accounted work exceeds \`MAX_NODES\`. This test is designed to distinguish the previous independent-counter behavior from the corrected shared-counter behavior.

## 4. Great Scale mapping

| Level | Mathematics | Science | Status |
|---|---|---|---|
| 5701–5710 | Total work is the sum of all relevant phases, not the maximum of separately bounded phases | Validation and copying both traverse the formula graph | Accounting gap identified |
| 5711–5720 | Per-phase bounds \(w_i\le B\) do not imply \(\sum_i w_i\le B\) | Independent counters can multiply the permitted aggregate work | Formalized |
| 5721–5730 | A shared mutable budget carries the invariant across phase boundaries | Copying must not silently restart node accounting | Shared budget passed into \`copyFormula\` |
| 5731–5740 | Recursive transformations inherit the same accounting state | Nested formula copying must consume the caller's internal budget | Recursive helper already shares supplied budget |
| 5741–5750 | All formula-bearing proof rules must obey one accounting policy | Assumptions, implication discharge, and disjunction introduction each copy formulas | Four call sites updated |
| 5751–5760 | A regression must distinguish old and new accounting semantics | A formula can fit one pass yet exceed the limit across validation plus copy | Adversarial test added |
| 5761–5770 | Resource limits bound a chosen work metric, not every physical cost | Node counts do not equal wall time, heap usage, or byte traffic | Scope of guarantee stated |
| 5771–5780 | Aggregate accounting is compositional only when helpers preserve the budget | New helpers must accept the internal budget explicitly or have a separately specified limit | Design rule recorded |
| 5781–5790 | A test source is a hypothesis until executed | The new test must run against the exact branch head | Test execution pending |
| 5791–5800 | Trusted verification needs controlled state and complete accounting coverage | This is a verifier-engineering result, not evidence of a new physical law | Integrated; CI evidence pending |

## 5. Verification record and limitations

Source inspection can establish that all four copy call sites pass the shared budget and that the new adversarial regression exists. It cannot establish that the regression executes successfully, nor that all other resource dimensions are complete.

The hosted Actions run previously inspected remained queued without step summaries, retrievable logs, or a receipt artifact. The local shell could not start in the prior execution session. Therefore this note does not claim that \`npm test\`, \`python3 test_descent.py\`, or a full build passed.

The node counter is an intentionally coarse work metric. It does not provide a hard-real-time guarantee and does not, by itself, bound every operation performed by JavaScript built-ins, garbage collection, stringification, or memory allocation. These remain separate assurance questions.

## 6. Conclusion

Level 5601 established that the verifier must own its counters. Level 5701 adds the necessary complementary condition: **every relevant internal phase must charge its work to the intended accounting scope**. A private counter that is repeatedly reset is still an incomplete aggregate budget.

The code now carries the shared budget through formula copying and includes a regression aimed at the prior gap. Full execution evidence is still required. No empirical quantum-geometric result follows from this software-hardening change.
