# Great Scale CXXXVI — Constrained Classification Optimization

## Model
There are \(G\) population units, observed values with fixed aggregate sum \(S\),
and a set of missing units \(i=1,\ldots,m\). Each missing unit has an allowed
stratum set \(A_i\). Binary assignment variables \(x_{ih}\in\{0,1\}\) satisfy

\[
\sum_{h\in A_i}x_{ih}=1,\qquad
m_h=\sum_i x_{ih},
\]

and count constraints \(a_h\le m_h\le b_h\). Each stratum has support
\([L_h,U_h]\). The endpoint objectives are

\[
\min_x\;\frac{S+\sum_hm_hL_h}{G},\qquad
\max_x\;\frac{S+\sum_hm_hU_h}{G}.
\]

The implementation enumerates all allowed assignments exactly. It is an exhaustive
reference solver for small cases, not a scalable mixed-integer programming engine.

## Synthetic test
Three missing units: units 1 and 2 may belong to A or B; unit 3 must belong to B.
Constraints require one or two missing units in each stratum. Supports are
A=[0,0.2], B=[0.4,1], observed aggregate sum S=30, and G=100.
Two assignments are feasible: (A,B,B) and (B,A,B). Each has one A and two B units.
Both yield lower endpoint \((30+1(0)+2(0.4))/100=0.308\) and upper endpoint
\((30+1(0.2)+2(1))/100=0.322\). Thus the robust interval is [0.308,0.322].

## Finding
Classification constraints can make a robust interval narrower than an unconstrained
assignment envelope, but only when those constraints are justified by external facts.
Optimization can exactly solve the stated problem; it cannot validate the assumptions
that define the feasible set.

## Test strategy
The test suite compares the solver against an independently written exhaustive oracle,
and checks infeasible constraints, unknown strata, and invalid support endpoints.
Tests are authored but have not been run in repository CI during this turn.
