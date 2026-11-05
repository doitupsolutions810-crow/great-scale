# Descent XCVI — Compensated metric determinant and numerical trust

## Finding

Scale covariance and positivity are not enough to establish numerical trust near a degenerate metric. For
\[
g=\begin{pmatrix}g_{11}&g_{12}\\g_{12}&g_{22}\end{pmatrix},
\qquad \det g=g_{11}g_{22}-g_{12}^{2},
\]
the determinant subtracts nearly equal products when the metric is ill-conditioned. A positive finite result can therefore still carry large relative error.

Use the exact family
\[
g_\varepsilon=\begin{pmatrix}1&1-\varepsilon\\1-\varepsilon&1\end{pmatrix}.
\]
Its exact determinant is \(\varepsilon(2-\varepsilon)\), with eigenvalues \(\varepsilon\) and \(2-\varepsilon\). Ordinary floating-point subtraction loses relative accuracy as \(\varepsilon\to0\).

## Correction

Both CommonJS and ESM bridges now:
- compute the normalized determinant with compensated products and subtraction, recovering low-order product bits in near-cancellation cases;
- calculate the smaller eigenvalue as \(\lambda_{\min}=\det(g)/\lambda_{\max}\), avoiding direct subtraction of nearly equal mean/spread terms;
- expose \(\kappa_2(g)=\lambda_{\max}/\lambda_{\min}\) as `metricConditionNumber`;
- expose `metricConditionStatus`: `well-conditioned`, `ill-conditioned`, or `numerically-unresolved`.

The status is diagnostic, not a claim that an ill-conditioned input is invalid. The thresholds are explicitly machine-precision heuristics: condition number above \(1/\sqrt{\epsilon_{mach}}\) is flagged ill-conditioned; a non-finite condition estimate or relative small eigenvalue at or below \(64\epsilon_{mach}\) is flagged numerically unresolved. The bridge does not add an epsilon to the determinant or silently regularize the metric.

Compensation improves arithmetic on the represented inputs; it cannot remove the intrinsic sensitivity of a nearly singular metric or restore precision absent from the input data.

## Great Scale map

For \(F_{12}=2\operatorname{Im}Q_{12}\), the normalized QGT ratio remains
\[
\chi=\frac{|F_{12}|}{2\sqrt{\det g}},\qquad
R=1-\chi^2=\frac{\det Q}{\det g}.
\]
The existing embedding is unchanged:
\[
S_Q=\frac{R}{4}=\frac{1-\chi^2}{4},\qquad
\Psi_Q=\frac{3-\sqrt5}{2}+S_Q.
\]
The conditioning channel is additional information alongside the scalar embedding. Under common positive scaling \((g,F)\mapsto(sg,sF)\), \(\chi\), the condition number, and the status are invariant when the scaled inputs remain representable.

## Regression and verification status

Regression cases were added for \(\varepsilon\in\{10^{-8},10^{-12},10^{-16}\}\), determinant/eigenvalue consistency, ill-conditioned and unresolved classification, and common-scale invariance. They have been committed to a working branch; execution status must be established from actual local or hosted test output, not inferred from the presence of tests.

Recent GitHub Actions runs for both repositories report failure, but the available job payloads have no steps and log downloads return `BlobNotFound`. That evidence does not identify a test failure or establish a passing test suite. See the pull request checks for subsequent evidence.
