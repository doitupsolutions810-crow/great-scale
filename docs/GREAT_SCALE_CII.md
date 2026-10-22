# Great Scale CII — Conditional-Mean Evidence Under Dependence

## Question

Can sequential evidence remain valid when Bernoulli observations are dependent,
provided the null still constrains each observation's conditional success
probability?

## Assumptions

Let \(X_t\in\{0,1\}\) and let \(\mathcal F_{t-1}\) contain all information
available before observing \(X_t\). The null is

\[
H_0:\quad \mathbb E[X_t\mid\mathcal F_{t-1}]\le q_0
\quad\text{almost surely for every }t,
\qquad 0<q_0<1.
\]

This permits dependence; it does not permit violating the conditional-mean
bound. The process must be defined relative to the actual information history.

## Construction and proof

Choose in advance a finite set of betting fractions
\(\lambda_k\in[0,1/q_0]\) and weights \(w_k\ge0\) with
\(\sum_k w_k=1\). Define

\[
M_{k,0}=1,\qquad
M_{k,t}=\prod_{i=1}^t[1+\lambda_k(X_i-q_0)].
\]

Nonnegativity follows because the smallest factor occurs at \(X_i=0\):
\(1-\lambda_kq_0\ge0\). Conditional expectation satisfies

\[
\mathbb E[1+\lambda_k(X_t-q_0)\mid\mathcal F_{t-1}]
=1+\lambda_k(\mathbb E[X_t\mid\mathcal F_{t-1}]-q_0)\le1.
\]

Therefore each \(M_{k,t}\) is a nonnegative supermartingale under \(H_0\).
The fixed mixture

\[
E_t=\sum_k w_kM_{k,t},\qquad E_0=1
\]

is also a nonnegative supermartingale. Ville's inequality gives

\[
\Pr_{H_0}\{\sup_{t\ge0}E_t\ge1/\alpha\}\le\alpha.
\]

Thus a threshold-crossing rule controls the probability of ever crossing
\(1/\alpha\) at level \(\alpha\), under the conditional-mean null.

## Example

Take \(q_0=0.5\), a single \(\lambda=1\), and outcomes \((1,1,0)\).
The successive factors are \(1.5,1.5,0.5\), so \(E_t\) is
\(1,1.5,2.25,1.125\). At \(\alpha=0.05\), the threshold is 20; this
short sequence does not cross it.

## Scope and cautions

- This is not an iid likelihood ratio and the \(\lambda_k\) values are
  betting strategies, not probability-model alternatives.
- The null must bound the conditional mean given the full past. A bound only
  on the unconditional average is insufficient.
- Betting fractions and weights in this implementation are fixed in advance.
  More general predictable, history-dependent fractions can be valid if
  chosen before the current outcome and if factor nonnegativity is preserved,
  but that extension is not implemented here.
- The mathematical guarantee assumes the conditional-mean model is correct.
  It does not establish that assumption empirically.
- This PR's local tests are not a claim that the complete repository suite or
  remote CI has passed.

## Great Scale mapping

CI used a one-sided iid Bernoulli null and a mixture of likelihood ratios.
CII replaces the iid sampling model with a conditional-mean constraint. The
invariant carried forward is nonnegative supermartingale evidence; the
model geometry changes from a fixed distribution family to a filtration-level
bound.
