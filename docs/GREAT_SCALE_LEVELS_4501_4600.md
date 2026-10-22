# Great Scale Levels 4501–4600 — Verification budgets must dominate all work

## Descent finding

The Level 4401–4500 hardening was not sufficient by itself. A follow-up audit found two ways the declared resource limits failed to bound the actual work:

1. The `orIR` inference path validated its embedded formula with a fresh default budget rather than the proof's shared budget. Repeating a large formula across nested proof steps could therefore reset the aggregate counter.
2. The truth-table oracle called the public evaluator for every valuation, and that evaluator revalidated each formula on every call. The semantic evaluation counter did not count this repeated validation work. A large formula that short-circuits during evaluation could trigger substantial unmetered preprocessing across many valuations.

The fix shares the aggregate node budget through `orIR`, validates the truth-table input once, then uses an internal evaluator that counts every AST node visited during semantic evaluation. This keeps input-validation work bounded by the input-node limit and repeated evaluation work bounded by the evaluation-step limit.

A further input-size boundary was added: atomic labels are limited to 4096 JavaScript string code units, proof-rule labels to 32, and proof objects with more than four fields are rejected before sorting their field names.

## Mathematical formulation

Let (V) be the verifier and let (W(x)) be the total work induced by input (x). A resource certificate is meaningful only if every potentially repeated operation is accounted for:

[
W(x)=W_{parse}(x)+W_{validate}(x)+W_{proof}(x)+W_{eval}(x)+W_{bind}(x).
]

A bound on one term, such as (W_{eval}le B), does not imply a useful total bound if another term can be repeated without a corresponding limit. A practical bounded checker therefore needs both an aggregate input bound and a global work counter for repeated execution phases, plus limits on individual string/field sizes.

This is an engineering invariant, not a new theorem of physics. The exact asymptotic and practical runtime guarantees still require implementation-level complexity analysis and measurements.

## Mitigation and tests

The branch now contains:
- shared proof/formula node accounting in `orIR`;
- one-time validation of truth-table inputs and a validated internal evaluator;
- a global 2,000,000-node semantic evaluation budget;
- 4096-code-unit atom limit and 32-character proof-rule label limit;
- early rejection of proof objects with more than four fields;
- regression tests for nested `orIR` budget resets, large-formula truth-table work, atom/rule label limits, and valid base cases.

A separate reference harness was executed after these changes: **5/5 targeted checks passed**. It covered the shared-budget adversary, the bounded truth-table stress case, the input-size precondition, atom/rule label limits, and a valid assumption/tautology. This is a reference execution of equivalent logic, not execution of the full committed `npm test` suite.

## CI and integration state

The latest GitHub Actions runs continue to fail immediately. The latest observed job has `runner_id: 0`, an empty runner name, no steps, no logs URL, and a two-second lifetime. Retrying the run produced the same no-step failure. This is strong evidence that the workflow job is not reaching a normal runner, but without a GitHub-hosted diagnostic/log record it does not identify the underlying cause with certainty.

The duplicate `blank.yml` workflow is removed on this branch. The remaining operational work is to use a functioning Actions runner or obtain repository/account-level Actions diagnostics. A green Vercel deployment/status is not evidence that the Node/Python verification suites ran.

## Success criteria

1. Every proof/formula path uses the same aggregate input budget.
2. Repeated evaluation does not repeat unmetered validation.
3. Oversized ASTs, labels, proof objects, and truth-table workloads fail closed.
4. Valid small examples still pass.
5. The exact commit's complete `npm test` and `python3 test_descent.py` commands run on a real CI runner and return success.
6. Logs/check-run metadata prove the test steps actually executed.
7. No merge or production promotion until criteria 1–6 are met.

## Great Scale candidate principle

**A verification limit must bound the whole path that consumes resources, not merely the step whose name appears in the counter.** A budget that can be reset, bypassed, or surrounded by unmetered repeated work is a label, not a bound.

The broader epistemic counterpart is that assurance cannot exceed the least-controlled step in its evidence pipeline. This is a candidate systems principle, not a physical quantum-geometry law.
