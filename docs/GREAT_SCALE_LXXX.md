# Great Scale LXXX — From Exact Invariants to Reliable Observation

## Descent question

LXXIX established that determinant parity of adjacent continued-fraction convergents encodes the side of the target. LXXX asks when that side can be certified from a bounded-error observation.

## Explicit model

Let x be the unknown true target, y its observed value, r the reference approximation, and epsilon >= 0 a known bound satisfying |y-x| <= epsilon. Then x lies in [y-epsilon, y+epsilon].

A side is certified if and only if

    |y-r| > epsilon

If y-r > epsilon, then x > r. If y-r < -epsilon, then x < r. If |y-r| <= epsilon, the interval touches or crosses r, so the bound alone cannot certify the side.

The certificate margin is m = |y-r| - epsilon. Unresolved cases are reported as certified=false and certified_side=0.

## Great Scale descent table

| Depth | Mathematics | Science |
|---|---|---|
| LXXVIII — Stable orbits and regime boundaries | Recurrence and boundedness | Distinguish stable repetition from change |
| LXXIX — Orientation–residual duality | Adjacent-convergent determinant fixes orientation parity | Exact arithmetic certifies orientation for continued fractions |
| **LXXX — Observation certificates** | certified iff abs(y-r) > epsilon; margin m=abs(y-r)-epsilon | A measured sign is reliable only when uncertainty cannot cross the reference |

## Pinned finding

| | Finding |
|---|---|
| Finding | The boundary between certified and unresolved side detection is exactly the uncertainty radius around the reference. |
| Where the 9-scale turns | The ninefold axis remains a discrete projection; the orbit axis now carries explicit observation uncertainty. |
| Where the finding lives | The admissible interval [y-epsilon, y+epsilon]. |
| Mathematics | Strict separation abs(y-r)>epsilon certifies sign(x-r). |
| Science | Declare the error model and bound before interpreting the sign. If the interval overlaps the reference, report unresolved. |
| Upper rungs | Exact invariant -> measured estimate -> uncertainty interval -> certified or unresolved conclusion. |

## Limits

This is a deterministic bounded-error statement, not a statistical confidence interval. It depends on the error bound being valid and inclusive of relevant measurement error and systematic bias. It does not establish reliability under unbounded noise without additional assumptions.

The code is a pure-Python research component. It does not by itself deploy the React/Vite UI or connect to physical sensors.
