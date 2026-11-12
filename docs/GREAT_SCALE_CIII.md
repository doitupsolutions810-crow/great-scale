# Great Scale CIII — Predictable Adaptive Evidence

## Question
Can the betting strategy change with history without losing the anytime-valid guarantee?

## Assumptions
Binary outcomes X_t in {0,1}, filtration F_(t-1), and null E[X_t | F_(t-1)] <= q0, with 0 < q0 < 1. At time t choose lambda_t using only F_(t-1), with 0 <= lambda_t <= 1/q0. The bet is fixed before the current outcome is seen.

## Proof
Set M_0=1 and M_t=M_(t-1)[1+lambda_t(X_t-q0)]. The factor is nonnegative because lambda_t*q0 <= 1. Since lambda_t is measurable with respect to the past,

E[M_t | F_(t-1)] = M_(t-1){1+lambda_t(E[X_t | F_(t-1)]-q0)} <= M_(t-1).

Thus M_t is a nonnegative supermartingale. Ville's inequality gives P_H0(sup_t M_t >= 1/alpha) <= alpha. A fixed convex mixture of such strategy-specific processes has the same property.

## Implementation
The Python implementation calls each strategy with an immutable tuple of past outcomes and validates the returned bet before applying the current outcome. Python cannot certify that a callback does not read hidden global state; callers must honor the predictable contract. Auditable deployments should use pure functions and log the history digest, selected bet, and outcome separately.

## Scope
The guarantee requires the conditional-mean null and predictable bets. A strategy selected after seeing the current outcome invalidates the proof. This is not empirical validation or a full-repository CI result.
