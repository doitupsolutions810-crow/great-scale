# Great Scale — Levels 8385–8396: Finite Phase Inputs

## Question

Does the phase-state function reject inputs that cannot define a finite phase, or can invalid values silently propagate through the geometry?

## Finding

The prior canonicalization established a range contract for ordinary finite values, but it did not validate the input domain. A non-finite time or rate makes the modulo operation produce NaN; downstream trigonometric and spatial values then become NaN as well. Finite operands can also overflow when multiplied, such as a very large finite time multiplied by a rate of 2. Canonical modulo arithmetic alone does not establish a valid numerical state.

## Integrated invariant

For a valid call, time t, rate r, and scaled time tr must all be finite. Invalid inputs fail closed before geometry is calculated. A zero rate remains valid and produces a stationary phase; negative rates remain valid and are normalized into the canonical interval.

`t, r, tr ∈ ℝ_finite  ⇒  φ(t,r) = ((tr mod 1) + 1) mod 1 ∈ [0,1)`

This is a numerical-domain contract, not a claim about physical time.

## Integration

- Added finite checks for time and rate, plus a post-multiplication finite check, in the ES-module and CommonJS implementations.
- Added equivalent guards to the Python reference.
- Added regression cases for NaN, positive/negative infinity, multiplication overflow, zero rate, negative rate, and ESM/CommonJS agreement.
- The canonical phase range and periodicity tests from Levels 8373–8384 remain in place.

## Great Scale table

| Level | Mathematics | Science / engineering | Status |
|---|---|---|---|
| 8385–8387 | Define the valid numerical domain before evaluating phase. | Non-finite inputs otherwise propagate into invalid spatial coordinates. | Guard integrated in JS and Python source. |
| 8388–8390 | Require t, r, and tr to be finite. | Reject overflow before trigonometric and geometry calculations. | Regression cases added; runtime pending. |
| 8391–8393 | r = 0 implies φ = 0; negative r still maps to [0,1). | Preserve legitimate stationary and reverse-time trajectories. | Regression cases added. |
| 8394–8396 | Domain validity precedes canonical representation. | Canonicalization cannot repair an undefined/non-finite input state. | Source edits require repository-suite execution. |

## Verification boundary

The edits and regression cases are committed through GitHub's file-update API on the research branch. This environment has not executed the repository's Node.js or Python suites. Source presence is not a runtime pass. Exact-head CI remains blocked by the previously observed runner condition, and PR #89 remains draft/unmerged.

## Profound finding

**A canonical representation is only meaningful after the input domain is valid.** The robust sequence is domain validation → finite arithmetic → canonicalization → geometry. Omitting the first two steps lets a well-normalized formula still emit invalid states.
