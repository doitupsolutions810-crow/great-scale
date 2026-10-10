# Great Scale CXXXIV — Robust Bounds with Uncertain Stratum Membership Counts

## Question

What if the total number of missing units is known, but their stratum membership is not?

## Model

Assume observed units' stratum membership and observed sums are known. For each stratum (h), the number of missing units (m_h) is only known to lie in ([a_h,b_h]), and the total missing count (M) is known:
\[
a_h\le m_h\le b_h,\qquad \sum_hm_h=M,\qquad m_h\in\mathbb{Z}.
\]
Each stratum has support ([L_h,U_h]), valid for every missing unit assigned to it. The population denominator (G=n_{obs}+M) is therefore fixed.

For any feasible allocation (m=(m_1,\ldots,m_H)), the mean is bounded by
\[
\mu_L(m)=G^{-1}\sum_h(S_h+m_hL_h),\quad
\mu_U(m)=G^{-1}\sum_h(S_h+m_hU_h).
\]
Uniform bounds across all feasible assignments are
\[
\boxed{\mu_L^{rob}=\min_{m\in\mathcal M}\mu_L(m),\qquad
\mu_U^{rob}=\max_{m\in\mathcal M}\mu_U(m),}
\]
where (mathcal M) is the set of integer allocations satisfying the count constraints. This is a small finite optimization problem; the reference implementation enumerates feasible allocations exactly.

## Synthetic test

Two strata have 40 observed units each, observed sums 2 and 20. There are 120 missing units in total. Each stratum may receive 40–80 missing units. Supports are [0,0.2] for A and [0.4,1] for B.

For the lower endpoint, the worst allocation is (80,40):
\[
(2+80\cdot0+20+40\cdot0.4)/200=0.19.
\]
For the upper endpoint, the worst allocation is (40,80):
\[
(2+40\cdot0.2+20+80\cdot1)/200=0.51.
\]
Thus the robust interval is [0.19,0.51], width 0.32. If counts were fixed at (60,60), the interval would be [0.23,0.47], width 0.24. Membership uncertainty widens the interval by 0.08.

## Profound finding

Even when every subgroup support is valid, uncertain assignment of missing units can consume some or all of the precision gained by stratification. The robust target is the extremum over all admissible count allocations. A result computed under a single preferred allocation is not robust to classification uncertainty.

## Test status

Unit tests cover worst-case allocations, infeasible totals, invalid supports, and disclosure of assumptions. These tests are authored but have not been run in CI as part of this integration.

## Great Scale ladder

- CXXXII — Justified stratum supports.
- CXXXIII — Robust bounds under uncertain support endpoints.
- **CXXXIV — Robust bounds under uncertain missing-unit stratum counts.**

## Next descent: CXXXV

Study partial uncertainty in observed-unit membership too. If observed sums move between strata under plausible reclassification, the extrema must optimize both the assignment of observed values and missing counts. The scientific question becomes: which classification facts are necessary to preserve the narrowing guarantee?
