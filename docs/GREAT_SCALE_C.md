# Great Scale C — Composite Nulls and Robust Fixed-Sample Evidence

## Descent question
XCIX mixed several predeclared alternatives against one fixed null. What changes when the null itself is a finite set of plausible Bernoulli rates?

## Model and assumptions
Observations are iid Bernoulli at a **fixed, predeclared sample size** n. The finite null set is Q0={q1,...,qm}; alternatives are p1,...,pK with fixed weights wk>=0 summing to one. These probabilities and weights must be chosen before inspecting the observations. Correlated observations, adaptive sample size, or an unvalidated model registry are outside this guarantee.

Let s=sum(xi). Define the mixture-alternative likelihood
N(x)=sum_k wk p_k^s(1-p_k)^(n-s)
and the worst-case null likelihood
D(x)=max_{q in Q0} q^s(1-q)^(n-s).
The statistic is E(x)=N(x)/D(x), provided D(x)>0.

## Fixed-sample validity
For every q in Q0, D(x)>=P_q(x). Therefore pointwise N(x)/D(x)<=N(x)/P_q(x) whenever P_q(x)>0. Taking expectation under q:
E_q[E(X)] = sum_x P_q(x) N(x)/D(x) <= sum_x N(x)=1.
The zero-probability boundary cases are handled by rejecting samples impossible under every null model rather than silently assigning an infinite ratio. Thus E is a fixed-sample e-value under each member of the declared finite null set.

A threshold E>=1/alpha supports a level-alpha fixed-sample test by Markov's inequality. This result does **not** provide an anytime-valid guarantee: changing denominators with n need not create a supermartingale, so Ville's inequality must not be applied to this statistic over repeated looks.

## Decision gate
If the iid assumption, fixed sample size, or predeclared model set is not confirmed, report ASSUMPTIONS_NOT_CONFIRMED rather than a statistical rejection. A low E-value means insufficient evidence, not proof that the null is true.

## Worked example
Use observations [1,1,1], Q0={0.4,0.5,0.6}, alternatives {0.8,0.2}, equal weights. The implementation computes the mixture likelihood divided by the largest likelihood among the three null rates. The exact result is recorded in artifacts/c_demo.json and is intentionally generated from the implementation rather than guessed here.

## Great Scale mapping
- XCVI: separate construction and validation evidence.
- XCVII: repeated tuning changes the evidential role of held-out data.
- XCVIII: sequential likelihood-ratio process for one fixed null/alternative pair.
- XCIX: fixed mixture over alternatives for a fixed null.
- C: robustness over a finite composite null at one predeclared sample size.

## Limitations / next descent
This is not a general solution for continuous composite nulls, arbitrary dependence, model misspecification, or optional stopping. The next rung should investigate predictable betting strategies that remain supermartingales for every null parameter, or a valid conditional model for dependence, with proof and exhaustive finite-state tests.
