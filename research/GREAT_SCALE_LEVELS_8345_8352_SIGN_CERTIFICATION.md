# Great Scale Descent — Levels 8345–8352
## Sign certification under bounded uncertainty

**Status:** mathematical specification and deterministic regression proposal. Not a physical or quantum claim.
**Predecessor:** Levels 8337–8344, orientation identifiability boundary.
**Question:** once a signed channel is retained, when can its sign be certified robustly rather than merely reported?

## 1. Observation model

Let the true signed quantity be C and the estimate be Ĉ, with a defensible absolute-error bound δ ≥ 0:

|Ĉ − C| ≤ δ.

Then the true value lies in the interval I = [Ĉ − δ, Ĉ + δ]. The sign is certified positive only if the whole interval is strictly positive; certified negative only if the whole interval is strictly negative. If zero belongs to I, the sign is not certified by this bound.

Equivalently:
- positive certificate: Ĉ − δ > 0;
- negative certificate: Ĉ + δ < 0;
- otherwise: unresolved.

The common shorthand |Ĉ| > δ is exactly the strict sign-stability condition for a symmetric error interval. At |Ĉ| = δ, the interval touches zero and the strict sign is not certified.

## 2. What this proves—and does not prove

This is a direct interval-arithmetic result, conditional on the error bound being valid. It does not establish that δ is calibrated, that a numerical solver converged, that a topological invariant is defined, or that the chosen model matches a physical system.

For a numerical Chern number or related topological quantity, a complete evidence package must additionally state:
1. model and parameter values;
2. whether the relevant spectral gap remains open;
3. grid/discretization and refinement sequence;
4. sign/orientation convention;
5. solver and code revision;
6. uncertainty/error-estimation method and coverage;
7. result status: certified, unresolved, invalid, or not computed.

An integer-looking output is not, by itself, a convergence certificate. A gap closing can invalidate the invariant's assumed regime even if the reported number appears stable at one resolution.

## 3. Minimal example

For Ĉ = 0.08 and δ = 0.03, I = [0.05, 0.11], so the sign is certified positive under the stated bound.

For Ĉ = 0.02 and δ = 0.03, I = [-0.01, 0.05], which contains zero; the sign is unresolved.

If the uncertainty bound is missing or unvalidated, the correct status is **uncertainty unbounded / sign uncertified**, not positive or negative.

## 4. Great Scale mapping

| Level | Mathematical operation | Scientific meaning | Required evidence |
|---|---|---|---|
| 8345 | Estimate Ĉ and error bound δ | Separate value from confidence in value | Explicit units and uncertainty source |
| 8346 | Construct I = [Ĉ−δ, Ĉ+δ] | Propagate bounded uncertainty | Interval arithmetic |
| 8347 | Test I ⊂ (0,∞) or I ⊂ (−∞,0) | Certify orientation sign only when zero is excluded | Strict inequality |
| 8348 | Treat 0 ∈ I as unresolved | Do not force a binary classification | Boundary cases |
| 8349 | Bind model, grid, convention, code SHA | Make result reproducible and interpretable | Complete provenance |
| 8350 | Check gap/model assumptions | Verify invariant is defined in the assumed regime | Gap and parameter audit |
| 8351 | Refine discretization and compare | Detect numerical instability | Multi-resolution comparison |
| 8352 | Gate promotion on evidence class | Keep algebraic result, numerical result, and physical claim separate | Explicit acceptance ledger |

## 5. Executable contract

The companion test is deliberately limited to the interval-sign rule. It must check:
- robust positive and negative examples;
- intervals crossing zero;
- intervals touching zero at either endpoint;
- zero uncertainty with a nonzero estimate;
- rejection of negative or non-finite uncertainty inputs;
- the rule that an absent error bound cannot produce a certified sign.

This tests the logic of the rule, not the calibration of an actual solver's error estimate.

## 6. Profound finding

**A signed channel restores distinguishability; a validated uncertainty bound determines whether its sign is knowable from the estimate.** These are two separate gates. Identifiability without uncertainty control can still produce overconfident labels; uncertainty control cannot repair a channel that discarded the sign in the first place.

Promotion rule: do not label an orientation/topological phase certified unless the signed channel is independently defined, the uncertainty interval excludes zero, and the model/discretization assumptions are evidenced. Otherwise preserve the numeric estimate with status unresolved or uncertified.
