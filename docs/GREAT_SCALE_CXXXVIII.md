# Great Scale CXXXVIII — Dynamic Programming with Verified Bounds

## Motivation
CXXXVII established that exactness requires complete feasible-set accounting. Full
assignment enumeration can examine up to \(\prod_i |A_i|\) assignments. Many
assignments differ only in unit identities but produce the same stratum-count vector.
Because the objective depends on counts, those assignments can be merged.

## State and recurrence
Let \(n\) be the number of strata and \(m\) missing units. A DP state is
\(v=(m_1,\ldots,m_n)\), the count vector after processing some units. For each
unit \(i\), transition from \(v\) to \(v+e_h\) for every permitted stratum
\(h\in A_i\), subject to upper count limits. After all units are processed,
retain states satisfying every lower count limit.

For any feasible count vector,
\[
L(v)=\frac{S+\sum_hm_hL_h}{G},\qquad
U(v)=\frac{S+\sum_hm_hU_h}{G}.
\]
Minimizing \(L(v)\) and maximizing \(U(v)\) over feasible states gives the
same endpoints as exhaustive assignment enumeration, since the objectives depend
only on the count vector.

## Synthetic verification
Twelve units may each belong to A or B. Supports are A=[0,0.2] and B=[0.4,1],
with no binding count constraints, \(G=100\), and \(S=10\). There are
\(2^{12}=4096\) unit assignments but only 13 distinct count vectors, indexed
by the number of A assignments from 0 through 12. The DP test checks that these
states suffice to compute the extrema and that state processing remains below 100.

## Finding
The correct compression target is not the assignment itself but the sufficient
state for the objective and constraints. When counts fully determine feasibility
and endpoint values, merging assignments by count vector preserves the exact bounds
while reducing redundant work. This is not universally polynomial: the count-state
space can still grow combinatorially with the number of strata and units.

## Verification
Tests compare DP endpoints to the exact enumerator on the corrected CXXXVI example,
test a 12-unit state-collapse case, and exercise infeasibility and invalid supports.
Repository tests are authored but have not been run in CI during this turn.
