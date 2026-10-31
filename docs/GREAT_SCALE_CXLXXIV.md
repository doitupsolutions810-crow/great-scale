# Great Scale CXLXXIV — Minimal Counterexample Contract

## Finding
A failed invariant is easier to investigate when the smallest reproducing case is retained. CI failure status without accessible logs leaves the failure unexplained; a deterministic counterexample reducer addresses the next step after a failure can be reproduced.

## Definition
For a finite ordered case (C) and deterministic predicate (F(C)), where (F(C)=mathrm{true}) means the failure reproduces, seek a subsequence (C^*\subseteq C) such that:
[
F(C^*)=\mathrm{true}
]
and for every single removable element (x\in C^*):
[
F(C^*\setminus\{x\})=\mathrm{false}.
]

This is **1-minimality**, not global minimum cardinality. The greedy delta-debugging algorithm preserves order and is deterministic for a deterministic predicate, but may not find the globally shortest counterexample.

## Integration
- Add `cxlxxiv_counterexample_minimization.py`.
- Add tests for removing irrelevant elements, rejecting non-failing initial inputs, and checking 1-minimality.
- The reducer is generic; callers must provide a reliable predicate that reproduces the specific model/test failure.

## Scientific interpretation and limits
The reducer improves diagnosis, not truth. A minimized failing example can reveal a missing assumption or implementation defect, but does not by itself prove a general theorem false. If the predicate is flaky or environment-dependent, the minimizer's result is not trustworthy.

## Validation status
Tests are authored and have not been executed in this session. CI logs for prior failures remained unavailable from the GitHub job-log endpoint. No claim is made that the CI issue is resolved.
