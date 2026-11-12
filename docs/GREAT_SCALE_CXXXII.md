# Great Scale CXXXII — Sharper Bounds from Justified Strata

## Descent question

Can the sharp global support interval be narrowed without returning to an empirically calibrated auxiliary margin?

## Mathematical result

Let the finite population be partitioned into strata (h=1,ldots,H). Stratum (h) has known size (G_h), observed sum (S_h), and (m_h) missing outcomes. Assume every missing outcome in that stratum lies in a defensible support interval ([L_h,U_h]). With (G=sum_h G_h),

\[
\boxed{\mu_L=\frac{1}{G}\sum_h(S_h+m_hL_h),\qquad
\mu_U=\frac{1}{G}\sum_h(S_h+m_hU_h).}
\]

The interval is sharp under these assumptions: assigning every missing value in stratum (h) to (L_h) attains the lower endpoint; assigning them all to (U_h) attains the upper endpoint. No narrower interval can be guaranteed from these assumptions alone.

A common global support ([L,U]) is the special case (L_h=L), (U_h=U). Stratification tightens the interval when its valid subgroup restrictions exclude values that the global support would otherwise permit. Merely naming groups does not justify narrower supports.

## Deterministic synthetic test

Two strata, each with population 100 and 40 observed outcomes:

- Stratum A: observed sum 2; support [0, 0.2]; 60 missing.
- Stratum B: observed sum 20; support [0.4, 1]; 60 missing.

Observed total = 22, population = 200, missing total = 120.

Stratified bounds:
\[
\mu_L=(2+60\cdot0+20+60\cdot0.4)/200=0.23,
\]
\[
\mu_U=(2+60\cdot0.2+20+60\cdot1)/200=0.47.
\]

Global [0,1] support bounds:
\[
[22/200,(22+120)/200]=[0.11,0.71].
\]

Widths: 0.24 versus 0.60, a 60% reduction in interval width. This is a deterministic constructed example, not evidence that the support assumptions are valid in a real application.

## Scientific interpretation

The gain comes from information about *where missing outcomes can lie*, not from the act of stratifying or from a statistical confidence claim. The guarantee is conditional on correct population counts, observed values, a genuine partition, and valid support limits. If even one missing outcome can fall outside its assigned support, the nominal guarantee can fail.

## Test status

The repository includes unit tests for the numerical example, endpoint attainability, rejection of observations outside declared supports, and invalid counts. These tests are authored but are not represented as executed by CI here. The deterministic arithmetic above is independently checkable.

## Great Scale ladder

- CXXIX — Held-out margin transfer: auxiliary margins do not automatically transfer.
- CXXX — Independent calibration and validation: calibration success can fail on held-out populations.
- CXXXI — Sharp global support bounds: guaranteed but potentially wide under valid common support.
- **CXXXII — Justified stratum supports: recover sharpness while narrowing the interval when external subgroup restrictions are valid.**

## Next descent

CXXXIII should treat support limits as uncertain sets rather than fixed truths, propagate each stratum's admissible limit range conservatively, and test the exact point at which tightening disappears. The key criterion is coverage of every admissible support configuration, not average simulation performance.
