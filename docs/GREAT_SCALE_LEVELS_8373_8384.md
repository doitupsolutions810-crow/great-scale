# Great Scale — Levels 8373–8384: Canonical Periodic Phase

## Question

Does periodic phase have a canonical representation in each Great Scale implementation?

## Finding

JavaScript's remainder operator can return a negative result for a negative dividend, whereas Python's modulo with a positive divisor produces a nonnegative result. For (r=0.85) and (t=-0.25), ((tr)\%1) is (-0.2125) in JavaScript and (0.7875) in Python. These values are equivalent modulo one, but their representations differ and may affect consumers expecting ([0,1)).

## Integrated invariant

Both JavaScript modules and the Python reference now normalize phase using the equivalent of:

[
\phi(t)=((tr)\%1+1)\%1
]

The invariant is (0\leq\phi(t)<1). For positive (r), the phase repeats after period (1/r), subject to floating-point tolerance.

Regression tests cover negative times, canonical bounds, ESM/CommonJS parity, and phase periodicity.

## Great Scale table

| Level | Mathematics | Science / engineering | Status |
|---|---|---|---|
| 8373 | Remainder semantics differ for negative values. | Cross-language representations diverged for negative time. | Source finding. |
| 8374 | Require (\phi(t)\in[0,1)). | Unit-circle phase has a canonical range. | Integrated in JS and Python. |
| 8375–8378 | Compare ESM and CJS at negative times and check bounds. | Same state should have the same representation across JS interfaces. | Regression cases added. |
| 8379–8382 | Require (\phi(t+1/r)\approx\phi(t)). | Equivalent cycle positions should agree within tolerance. | Regression cases added. |
| 8383–8384 | Mathematical equivalence differs from representation equality. | Canonicalization makes the representation contract explicit. | Runtime suites unverified. |

## Verification boundary

Source and regression edits are committed to the research branch. Repository Node.js and Python suites have not been executed in this environment. No runtime pass is claimed. PR #89 remains draft and unmerged while CI execution and branch divergence remain unresolved.

## Profound finding

When a mathematical state crosses language boundaries, the abstract object and its machine representation are distinct layers. Canonicalizing phase reduces ambiguity; independent execution is still required to establish implementation correctness.
