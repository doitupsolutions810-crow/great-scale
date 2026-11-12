# Great Scale CXXIV — Stratified Partial-Identification Bounds

## Question
Can valid auxiliary strata tighten finite-population bounds when some cluster outcomes are missing, without assuming the missing outcomes resemble observed ones?

## Mathematics
For stratum h, let G_h be its known frame count, n_h the observed count, m_h=G_h-n_h the missing count, S_h the sum of observed outcomes, and [L_h,U_h] valid outcome limits for that stratum. With G=Σ_h G_h:

\[
\mu_L=\frac{1}{G}\sum_h(S_h+m_hL_h),\qquad
\mu_U=\frac{1}{G}\sum_h(S_h+m_hU_h).
\]

The interval is sharp under the stated assumptions: each missing value may attain its stratum's lower or upper limit. Its width is

\[
W=\frac{1}{G}\sum_hm_h(U_h-L_h).
\]

If every stratum uses the same global limits, this reduces to the unstratified bound. Valid narrower stratum limits can reduce width; inaccurate limits can invalidate coverage.

## Synthetic experiment
A deterministic 240-cluster population uses two strata: A outcomes in {0, 0.25}, B outcomes in {0, 0.125}; bounds are [0,0.25] and [0,0.125]. A seeded Bernoulli observation process uses probabilities 0.35 and 0.65. The demo compares stratum-specific bounds to the global [0,0.25] interval. This is a designed synthetic illustration, not empirical evidence.

## Assumptions and limits
- Stratum membership and total frame counts are known.
- Observed outcomes are exact and lie within their stated stratum bounds.
- The bounds are genuine for every missing unit.
- These are identification bounds, not confidence intervals; sampling uncertainty in estimated bounds is not included.
- Auxiliary strata help only when they justify narrower valid outcome ranges or otherwise add constraints.

## Great Scale finding
Missingness need not be solved by guessing missing values. Valid structure about the population can reduce uncertainty while preserving honest worst-case bounds. The scientific bottleneck moves from estimating a point to validating the auxiliary constraints.
