# Great Scale CXXVI — Calibrating Auxiliary Bounds

## Question
Can auxiliary observations establish subgroup limits that safely constrain outcomes for the entire finite population?

## Procedure
For each stratum, an auxiliary sample supplies a minimum and maximum. An explicit nonnegative margin expands these observed extrema:
\[
L_h=\max(0,\min(A_h)-\eta),\qquad U_h=\max(A_h)+\eta.
\]
The bounds then use the CXXIV finite-population formula:
\[
\mu_L=G^{-1}\sum_h(S_h+m_hL_h),\qquad
\mu_U=G^{-1}\sum_h(S_h+m_hU_h).
\]

The margin \(\eta\) is a sensitivity parameter, not an automatically valid statistical correction. Empirical extrema do not guarantee population limits: an auxiliary sample can miss a rare extreme. Without distributional assumptions, a known physical bound, or a calibrated statistical guarantee, no finite sample alone proves that its observed minimum and maximum bound all unobserved outcomes.

## Exact counterexample
Auxiliary values [0,0,0] produce an observed maximum of 0. A four-unit population [0,0,0,1] has true mean 0.25, but the naive auxiliary-derived upper bound is 0. The data-derived constraint therefore fails. This is a deterministic counterexample, not a stochastic claim.

## Scientific finding
The bound calculation is only as valid as the limits fed into it. Estimating limits and proving limits are different operations. The next valid advance requires either domain-guaranteed support limits or an explicit calibration model with stated coverage assumptions.
