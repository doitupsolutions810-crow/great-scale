# Great Scale Levels 5601–5700: Verifier-Owned Resource Budgets

**Track:** \`research/kernel-hardening-4401-4500\`  
**Scope:** public proof-kernel API, resource accounting, and caller-controlled state  
**Implementation status:** public wrappers now allocate their own counters; adversarial regression tests are committed but full repository execution remains unverified.

## 1. Deeper repository finding

After stabilizing checked results against mutation, a further source review found that the resource counters themselves crossed the public API boundary.

Before this change, the exported \`validateFormula(formula, depth, budget)\`, \`check(proof, budget)\`, and \`evalF(formula, env, steps)\` signatures let a caller provide mutable internal accounting state. For example, a caller could pass a negative node count to \`check\` or \`validateFormula\`, or pass a getter-backed \`steps.count\` object to \`evalF\`. This meant that the implementation's resource policy depended in part on caller-controlled state.

The finding is more general than a specific counter:

> **A verifier cannot enforce a resource limit if an untrusted caller can choose or mutate the accounting state that defines that limit.**

The limits were constants, but the mutable counters that enforced them were previously caller-injectable.

## 2. Mathematical formulation

Let \(I\) be a public verifier entry point, \(x\) an input, \(B\) the configured resource bound, and \(s\) the accounting state. A resource contract requires

\[
\operatorname{Work}(I,x)\leq B
\]

for every accepted invocation within the declared input and runtime model. If the public interface permits the caller to choose \(s_0\), and the guard checks \(s_0+\operatorname{Work}\leq B\), then choosing \(s_0<0\) can weaken the effective bound.

The desired API invariant is

\[
s_0 = s_{\mathrm{fresh}} \quad\text{and}\quad
s_{\mathrm{fresh}}\notin\text{caller-controlled inputs}.
\]

This does not prove that every possible execution has a precise wall-clock bound. It means the verifier initializes its own logical counters, and callers cannot weaken those counters through optional arguments or accessor-backed accounting objects.

## 3. Integrated change

The current branch separates public entry points from internal helpers:

- **\`validateFormula(formula)\`** now creates a fresh node budget and delegates to internal recursive validation. The public API no longer exposes depth or budget controls.
- **\`check(proof)\`** now creates a fresh proof/formula node budget and delegates to \`checkInternal\`. \`checkBound\` uses the internal helper to preserve its intended aggregate accounting across claim context and proof validation.
- **\`evalF(formula, env)\`** now creates its own evaluation counter and delegates to \`evalFInternal\`. A caller-supplied third argument is no longer consumed.
- Internal recursive paths use internal helpers so nested validation shares the intended budget rather than accidentally resetting it.
- Added three regression cases to \`test_proof_kernel.js\`: a large formula with a negative supplied budget, a large proof with a negative supplied budget, and a getter/setter-backed caller counter that must not be touched by \`evalF\`.

This change keeps the exported function names and ordinary two-argument/one-argument usage intact while removing public control over internal accounting state.

## 4. Great Scale mapping

| Level | Mathematics | Science | Status |
|---|---|---|---|
| 5601–5610 | A resource guard is meaningful only if its initial state is controlled | Caller-supplied counters can undermine otherwise fixed resource limits | API flaw identified |
| 5611–5620 | Require \(s_0=s_{\mathrm{fresh}}\), not an arbitrary caller value | Negative or manipulated counters can weaken node/work checks | Public wrappers now create fresh state |
| 5621–5630 | Public and internal signatures have distinct trust roles | Internal recursion needs shared accounting; external callers should not control it | \`validateFormulaInternal\` and \`checkInternal\` introduced |
| 5631–5640 | Aggregate resource accounting must remain shared across related claim/proof validation | A wrapper refactor must not reset budgets inside recursive paths | \`checkBound\` retains internal shared budget |
| 5641–5650 | Work counters are state, not inert configuration | Accessor-backed counter objects can execute code or manipulate observed accounting | \`evalF\` owns its counter |
| 5651–5660 | Adversarial tests should attempt to violate the budget contract | Large formula/proof inputs with negative external counters test the boundary | Three regression cases authored |
| 5661–5670 | Resource limits, depth limits, and logical correctness are independent properties | A bounded run can still be logically wrong; a sound rule can still be exposed to resource exhaustion | Assurance obligations separated |
| 5671–5680 | Public API shape is part of the verifier's security model | Optional parameters can expose internals even when documentation calls them implementation details | Exported wrappers narrowed |
| 5681–5690 | Source presence does not establish execution outcome | Regression source must run on the exact commit | Test execution pending |
| 5691–5700 | Trusted verification requires controlled inputs, internal accounting, and stable certificates | This is a software resource-accounting result, not a physical quantum-geometry result | Integrated; CI evidence pending |

## 5. Verification record and limitations

Source inspection confirms the public wrappers, internal shared-budget calls, and three new regression cases are present. The tests deliberately use moderately large but shallow trees so the node budget, rather than recursion depth, is the expected failure mechanism.

The repository's hosted runner has repeatedly remained queued or failed before producing useful step summaries, logs, or a receipt artifact. The local shell could not start in the current session. Consequently this document does **not** claim that \`npm test\`, \`python3 test_descent.py\`, or a full build passed.

Required completion evidence remains an exact-head run with a nonempty step list, a real runner identity, successful JavaScript and Python suites, retrievable logs, and a same-run commit-bound receipt.

The API wrappers reduce accidental caller control over counters. They do not constitute an operating-system sandbox, do not establish a wall-clock hard-real-time guarantee, and do not cover hostile JavaScript Proxy behavior beyond the documented input domain.

## 6. Conclusion

The deeper result is that **a security limit is only as trustworthy as the state that enforces it**. A constant named \`MAX_NODES\` is not enough if a caller can inject the counter used by its guard. Public APIs should accept the proposition to be checked, while the verifier owns the bookkeeping required to check it.

The implementation now separates public wrappers from internal budget-carrying helpers and includes adversarial regression tests. Until those tests execute successfully on the exact committed SHA, the change remains integrated but not fully test-verified. No new physical law or empirical quantum-geometric finding follows from this work.
