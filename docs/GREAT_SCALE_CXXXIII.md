# Great Scale CXXXIII — Robust Tightening Under Uncertain Stratum Supports

## Question

Does stratified tightening survive when support endpoints are not known exactly?

## Robust construction

For each stratum, suppose admissible support endpoints satisfy
\[
L_h\in[L_h^-,L_h^+],\qquad U_h\in[U_h^-,U_h^+].
\]
For a bound valid uniformly over the stated endpoint uncertainty, use the outermost possible limits:
\[
\boxed{\mu_L^{rob}=G^{-1}\sum_h(S_h+m_hL_h^-),\quad
\mu_U^{rob}=G^{-1}\sum_h(S_h+m_hU_h^+).}
\]
This is conditional on every true stratum support being represented by the admissible endpoint ranges and on the missing values lying inside the corresponding support.

## The width criterion

The robust interval's width is
\[
W_{rob}=G^{-1}\sum_hm_h(U_h^+-L_h^-).
\]
The global-support interval width is
\[
W_{global}=G^{-1}M(U-L),\quad M=\sum_hm_h.
\]
Therefore robust stratification is strictly tighter exactly when
\[
\boxed{\sum_hm_h(U_h^+-L_h^-)<M(U-L).}
\]
This criterion depends on missing counts and admissible support spans—not observed sums. If all missing units have local spans equal to the global span, no width improvement is possible. If local spans are wider, stratification may worsen the interval. The mean location still depends on observed sums.

## Deterministic test

Two strata, each with population 100, 40 observed, 60 missing. Observed sums are 2 and 20. The outer admissible supports are [0,0.2] and [0.35,1].

Robust interval:
\[
[(22+60(0)+60(0.35))/200,\ (22+60(0.2)+60(1))/200]
=[0.215,0.47].
\]
Width = 0.255. The global [0,1] comparator is [0.11,0.71], width 0.60. Width reduction is 57.5%.

The synthetic test suite also includes an equality case: if the missing-mass-weighted local support span equals the global span, no width tightening occurs. These are deterministic tests, not empirical validation of the support assumptions.

## Profound finding

Stratification is not itself the source of precision. The gain is controlled exactly by the missing-mass-weighted admissible support span. This separates two questions: (1) are the restrictions scientifically defensible? (2) do they mathematically reduce uncertainty? Both must hold to claim a useful robust improvement.

## Great Scale ladder

- CXXXI — Sharp global support bounds: valid global range, possibly wide.
- CXXXII — Justified stratum supports: subgroup constraints can narrow bounds if valid.
- **CXXXIII — Uncertain stratum supports: widen to the outer admissible limits and test the exact width criterion.**

## Next descent: CXXXIV

Treat uncertainty about subgroup membership or population counts themselves. Derive bounds when units may be assigned to more than one stratum, and identify whether count uncertainty destroys the gain. The correct target is a worst-case bound over all allowed assignments, not a point estimate based on a preferred classification.
