# Great Scale LXXXIX — Distribution Shift, Evidence Expiration, and the Boundary of Transfer

## Descent question

LXXXVIII controls false discoveries during repeated search. LXXXIX asks whether a validated finding still applies after the environment changes. Historical evidence can be correct for its source distribution and still fail to predict deployment behavior.

## Definitions

Let \(P\) be the historical joint distribution of inputs and outcomes, \(Q\) the deployment joint distribution, and \(L(f(x),y)\) a loss satisfying \(0\le L\le M\). Define

\[
R_P(f)=\mathbb E_P[L(f(X),Y)],\qquad
R_Q(f)=\mathbb E_Q[L(f(X),Y)].
\]

For total variation distance

\[
d_{\rm TV}(P,Q)=\sup_A|P(A)-Q(A)|,
\]

the bounded-function inequality gives

\[
|R_Q(f)-R_P(f)|\le M d_{\rm TV}(P,Q).
\]

If \(R_P(f)\le r\) and a justified bound \(d_{\rm TV}(P,Q)\le\delta\) is available, then

\[
R_Q(f)\le\min\{M,r+M\delta\}.
\]

This is a transfer guarantee conditional on valid bounds and a bounded loss. It does not itself estimate the distance between distributions, and an input-only drift metric need not reveal changes in the conditional relationship between inputs and outcomes.

## Worked example

Assume loss is bounded by \(M=1\), historical risk has a valid upper bound \(r=0.05\), and a justified total-variation upper bound is \(\delta=0.10\). Then

\[
R_Q(f)\le 0.05+1(0.10)=0.15.
\]

If the acceptable risk limit is 0.12, the transfer is not certified under these bounds. This does not prove actual deployment risk exceeds 0.12; it means the current bound is too weak to certify compliance.

The maximum shift budget for risk limit \(\tau\), when \(r\le\tau\) and \(M>0\), is

\[
\delta_{\max}=\min\left(1,\frac{\tau-r}{M}\right).
\]

## Operational protocol

1. Track deployment outcomes and relevant data summaries; do not equate a change in input marginals with a complete measure of risk.
2. Distinguish covariate shift, label/prior shift, and concept shift. Each requires different assumptions and diagnostics.
3. Keep model validity, calibration validity, data provenance, and deployment context as separate versioned claims.
4. When the transfer bound exceeds the permitted risk, mark the evidence **TRANSFER NOT CERTIFIED**; increase monitoring, collect representative labels, recalibrate, or suspend high-impact automated actions as appropriate.
5. Revalidate after a material change or when monitoring signals exceed predeclared limits. Do not automatically retrain on drift signals without checking label quality and unintended feedback.
6. Recompute downstream risk and dependency analyses after an approved model or assumption change, retaining the previous version and audit trail.

## Pinned finding

**Evidence has a domain of validity.** Validation does not expire merely because time passes; it loses its deployment guarantee when the assumptions connecting historical and current distributions can no longer be defended.

## Scientific limits

A distribution-shift alert is not proof that predictive performance has degraded, and no alert is not proof that it has remained stable. Estimating total variation in high-dimensional settings is difficult. Guarantees require justified distance bounds, bounded loss, representative data, and uncertainty accounting. This rung is a formal design and illustrative example, not empirical validation of a deployed model.
