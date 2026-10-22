# Great Scale CXXXIX — State Sufficiency and Compression Audit

## Question
When is it mathematically safe to replace assignment enumeration with dynamic
programming over subgroup-count vectors?

## Sufficient conditions
Let each unit i have a fixed allowed-stratum set A_i. Process units in a fixed
order. Count-state compression is exact when:
1. the choices available for each unprocessed unit are independent of the identities
   of already-assigned units, except through any explicitly represented constraints;
2. feasibility can be determined from the final count vector; and
3. objective endpoints depend only on that count vector.

For the stratum-homogeneous additive bounds,
\[
L(v)=\frac{S+\sum_hm_hL_h}{G},\quad
U(v)=\frac{S+\sum_hm_hU_h}{G},
\]
these conditions hold for fixed allowed sets and count-only constraints. At a given
processing depth, two partial assignments with the same counts have the same
remaining units and therefore the same future transitions. They can safely merge.

## Test evidence design
The tests include asymmetric unit choices (one unit restricted to B), the CXXXVI
corrected example with endpoints [0.304, 0.322], and a 12-unit binary example:
4096 assignments collapse to 13 count states with endpoints [0.10, 0.22].
They also check rejection of infeasible constraints and empty choice sets.

## Boundary of the claim
This is not a universal compression theorem for arbitrary objectives. If a unit's
value differs by identity, if assignments interact, or if history affects future
eligibility, counts alone may not be sufficient. Such models need an expanded
state (for example, stratum-specific sums, interaction flags, or history variables).
The audit compares exact assignment-space and count-space endpoints for finite
test instances; it is not a formal proof of every possible model.

## Verification status
Tests are authored in this PR but have not been executed in CI/runtime during this
turn. Expected values are independently derivable from the displayed formulas.
