# Great Scale CI — Anytime-Valid Evidence for a One-Sided Composite Null

## Research question
Can the fixed-sample robustness at rung C be extended to sequential monitoring? Yes for a narrower, explicitly one-sided Bernoulli null, using a boundary likelihood-ratio process.

## Model
Assume observations X_t are iid Bernoulli(q), and the null is H0: q <= q0, with fixed q0 in (0,1). Choose alternative probabilities p_k in (q0,1] and fixed weights w_k >= 0 summing to one before observing data.

For each alternative p > q0, define
L_t(p;q0) = product_{i=1}^t (p/q0)^{X_i} ((1-p)/(1-q0))^{1-X_i}.
For any null q <= q0, the conditional expectation of the next likelihood-ratio factor is
q p/q0 + (1-q)(1-p)/(1-q0) <= 1,
because this expression is increasing in q when p > q0 and equals 1 at q=q0. Hence L_t is a nonnegative supermartingale under every null q <= q0.

The fixed mixture E_t = sum_k w_k L_t(p_k;q0) is also a nonnegative supermartingale with E_0=1. Ville's inequality therefore gives
P_q(sup_t E_t >= 1/alpha) <= alpha
for every q <= q0.

## What is new
This supplies an anytime-valid sequential guarantee for a one-sided composite null. It is not a solution for arbitrary finite null sets, two-sided alternatives, dependence, adaptive alternative selection, or model misspecification. It complements rung C rather than replacing it.

## Testing plan
The test suite enumerates every binary sequence of length five to check E_q[E_n] <= 1 for q=0.1, 0.4, and 0.6, and every sequence of length eight to check the threshold-crossing probability for q=0.2 and 0.6 at alpha=0.05. These are finite computational checks; the general guarantee rests on the conditional-expectation proof above.

## Great Scale mapping
XCIX: fixed mixture over alternatives for a simple null.
C: finite composite null, fixed-sample e-value.
CI: boundary likelihood-ratio mixture gives anytime-valid evidence for H0:q<=q0, under iid Bernoulli assumptions.

## Profound finding
Robust sequential certainty is possible when the null set has an order structure: its worst-case boundary calibrates a betting process that remains conservative throughout time. General composite nulls require their own construction and proof; this result must not be generalized beyond its assumptions.
