# Quantum Geometry Bridge — Great Scale

Status: additive mathematical bridge; not an empirical claim.

## Convention

For a smooth pure-state family, define
\[
Q_{\mu\nu}=\langle\partial_\mu\psi|
(I-|\psi\rangle\langle\psi|)|\partial_\nu\psi\rangle,
\quad g=\operatorname{Re}Q,
\quad F_{12}=2\operatorname{Im}Q_{12}.
\]
For two nondegenerate parameter directions, QGT positivity gives
\[
\det Q=\det g-\frac{F_{12}^2}{4}\geq0.
\]
Define the dimensionless curvature fraction
\[
\chi=\frac{|F_{12}|}{2\sqrt{\det g}},\quad 0\leq\chi\leq1.
\]
Then the normalized QGT residual is
\[
R=\frac{\det Q}{\det g}=1-\chi^2.
\]

## Exact Great Scale embedding

Set
\[
h_Q=\frac{1+\chi}{2}.
\]
Using the existing Great Scale law \(\operatorname{heat}(h)=h(1-h)\),
\[
S_Q=\operatorname{heat}(h_Q)
=\frac{1-\chi^2}{4}
=\frac{1}{4}\frac{\det Q}{\det g}.
\]
The existing cone law can be reused without altering the original phase-driven state:
\[
\Psi_Q=\mathrm{CONE}+S_Q,\qquad \mathrm{CONE}=\phi^{-2}.
\]
This preserves \(0\leq S_Q\leq1/4\) and \(\Psi_Q\geq\mathrm{CONE}\).
Saturated geometry (\(R=0\)) maps to zero geometric heat; zero curvature with a nondegenerate metric (\(R=1\)) maps to maximal heat \(1/4\).

## Interpretation and limits

- \(\chi\) is dimensionless and measures curvature relative to the metric-area bound.
- \(R\) is the fraction of the metric determinant left in the QGT Gram-determinant residual.
- \(S_Q=R/4\) is an exact encoding, not a new physical law.
- The bridge is defined only where \(\det g>0\); degenerate directions need separate treatment.
- Inputs violating \(|F_{12}|\leq2\sqrt{\det g}\) are rejected, except for configured floating-point tolerance.
- \(S_Q\) is a new derived channel. It does not replace the original phase-based \(h,S,\Psi\), or the ninefold involution.
- No material-specific prediction or experimental validation is claimed.

## Verification

Run npm test and python3 test_descent.py.
The JavaScript suite covers zero curvature, saturation, intermediate curvature, scale invariance, invalid curvature, and degenerate metrics.
