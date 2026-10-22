# Great Scale — Levels 5901–6000: bound derived proof-kernel work

## Finding

The kernel bounded proof/formula node visits, but derived operations were not charged to that node budget. In particular, implication introduction searched an accumulated assumption context with `findIndex` and compared each candidate using `JSON.stringify`; repeated discharge can rescan many long formulas. Context concatenation also copies intermediate arrays, and claim-bound context comparison serialized every formula before sorting. A finite AST-node count alone did not express the cost of these repeated operations.

This is a resource-accounting gap, not a claim of unbounded input or a demonstrated remote exploit. The existing limits bound node count, nesting depth, and individual atom length, but did not explicitly cap repeated context-comparison work.

## Integration

- Added a verifier-owned `MAX_KERNEL_WORK = 2,000,000` budget, separate from the input-node budget.
- Added structural `formulaEquals`, charging one unit per formula node and a length-proportional amount for string comparisons.
- Charged context concatenation, discharge-array copying/shifting, and every candidate slot examined during context-multiset matching against the same work budget, including already-matched slots.
- Replaced repeated JSON serialization in internal implication checks and claim-bound conclusion/context matching with budgeted structural comparisons. The exported compatibility helper `eq` remains available, but the proof-checking path no longer relies on it for these decisions.
- Added an adversarial regression with 2,100 long atom formulas and 100 nested discharges; it must fail closed with `kernel work budget exceeded` before completing an excessive comparison workload.

## Mathematics

Let (N) be the number of input nodes and (L) the maximum atom-string length. The prior node policy constrained (N \leq 10{,}000) and (L \leq 4{,}096), but repeated context search could still incur work on the order of
[
W_{\mathrm{compare}} = \sum_{j=1}^{d}\sum_{i=1}^{|\Gamma_j|} O(|F_{j,i}|),
]
where (d) is the number of implication discharges, \(\Gamma_j\) is the remaining context, and \(|F_{j,i}|\) includes formula structure and compared string lengths. The new accounting rejects when its charged derived work exceeds (B=2{,}000{,}000):
[
W_{\mathrm{charged}} \leq B
\quad\text{or the verifier rejects.}
]

This is an explicit bound on the charged operations, not a proof that every JavaScript runtime instruction, garbage-collection pause, allocation, or byte copied is exactly proportional to the counter. Those remain separate engineering concerns.

## Science and engineering interpretation

The result is about resource-bounded proof checking and adversarial algorithmic complexity. The budget is an engineering policy, not a theorem about wall-clock time. It does not establish a physical quantum-geometry model or provide empirical evidence for a new physical law.

## Evidence status

- Source integration: committed to the research branch.
- Regression: committed, but not executed in a local runtime.
- Verification: source-level inspection only until a runner executes the regression and full suites on this exact commit.
- Build: not verified.
- Hosted CI: the latest observed run failed without job steps/logs/artifacts; a new exact-head run must be inspected after these commits.
- Promotion: blocked. PR #89 remains draft and unmerged, and the branch is still 99 commits ahead / 2 behind `main`; reconcile the base divergence before promotion.
