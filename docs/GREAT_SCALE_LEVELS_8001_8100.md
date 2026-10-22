# Great Scale — Levels 8001–8100: distinguish scalar contraction from matrix dynamics

## Profound finding

The public model's `HYPOTHESIS` text claimed that the scalar `CONE = φ⁻²` and the matrix
`M = [[2,-1],[-1,1]]` were “the same contraction rate,” and described `M³ = CONE³`.
That statement is mathematically misleading if read as a claim about the matrix's full action.

The characteristic polynomial is
\[
\chi_M(\lambda)=\det(\lambda I-M)=\lambda^2-3\lambda+1,
\]
so the eigenvalues are
\[
\lambda_{\pm}=\frac{3\pm\sqrt5}{2}=\phi^{\pm2}.
\]
Since \(\phi^2>1\) and \(\phi^{-2}=\mathrm{CONE}\in(0,1)\), the matrix has one expanding eigendirection and one contracting eigendirection. It is not a global contraction by the scalar `CONE`.

The determinant is \(\det M=1\), consistent with the product of the reciprocal eigenvalues. The matrix can preserve area while expanding one eigendirection and contracting the other. That is hyperbolic/saddle-type linear dynamics, not uniform contraction.

## Integration

- Corrected the hypothesis statement in both `public/scale.js` and `public/scale.cjs`.
- Kept the module contracts aligned so the ESM and CommonJS descriptions match exactly.
- Extended `test_scale_module_parity.js` to compute the trace, determinant, discriminant, and eigenvalues from the exported matrix.
- Added assertions that the eigenvalues match \(\phi^2\) and `CONE`, and that one is greater than 1 while the other lies strictly between 0 and 1.
- The test remains part of the canonical `npm test` script through the module-parity integration.

## Mathematics

For
\[
M=\begin{pmatrix}2&-1\\-1&1\end{pmatrix},
\]
\[
\operatorname{tr}(M)=3,\qquad \det(M)=1,\qquad
\lambda^2-3\lambda+1=0.
\]
The roots are reciprocal:
\[
\lambda_+\lambda_-=1,\qquad
\lambda_+=\phi^2>1,\qquad
\lambda_-=\phi^{-2}=\mathrm{CONE}<1.
\]

For a vector decomposed into eigenvectors, \(v=a v_+ + b v_-\),
\[
M^n v=a\phi^{2n}v_+ + b\phi^{-2n}v_-.
\]
Unless the expanding component \(a\) is zero, the norm generally does not converge to zero. The scalar recurrence
\[
x_{n+1}=x_*+\mathrm{CONE}(x_n-x_*)
\]
does converge because its single error multiplier has magnitude below one. These are different dynamical systems and must not be conflated.

## Science and engineering interpretation

The finding separates two mathematically valid but different objects: a scalar contraction map and a two-dimensional linear transformation with reciprocal eigenvalues. Their shared appearance of \(\phi^{-2}\) means that this scalar is one eigenvalue of the matrix; it does not make the entire matrix a contraction by that factor.

This correction improves the model's mathematical specification. It is not empirical evidence for a physical mechanism or a new quantum-geometry law. Any physical interpretation would need a defined state space, observable mapping, units, and independent empirical tests.

## Great Scale mapping

| Level | Mathematics | Science / engineering meaning | Test / verification gate |
|---|---|---|---|
| 8001 | \(\chi_M(\lambda)=\lambda^2-3\lambda+1\) | Derive spectrum from the declared matrix | Compute trace, determinant, and characteristic polynomial |
| 8010 | \(\lambda_+=\phi^2>1\), \(\lambda_-=\phi^{-2}<1\) | Distinguish expansion from contraction | Assert both eigenvalues and their inequalities |
| 8020 | \(\det M=\lambda_+\lambda_-=1\) | Reciprocal expansion/contraction is area-preserving in the linear model | Check determinant and eigenvalue product |
| 8030 | Scalar error scales as \(\mathrm{CONE}^n\); matrix components scale as \(\phi^{\pm2n}\) | Do not transfer scalar convergence claims to matrix dynamics | Keep separate regression assertions and documentation |
| 8040 | ESM hypothesis = CJS hypothesis | Same claim must be published consistently in both module formats | Exact hypothesis parity check |

## Test / verify / run / build status

- **Source integration:** both module formats now use the corrected matrix statement.
- **Regression added:** matrix trace, determinant, eigenvalue identities, and expanding/contracting inequalities are checked by the parity test.
- **Static source review:** the updated test contains the spectral assertions and the shared hypothesis string was corrected in both files.
- **Repository test run:** not verified. The available execution runtime returned an error, so `npm test` was not run successfully in this session.
- **CI:** no pull-request workflow run was returned for the latest source SHA when checked. No test-pass claim is made.
- **Build:** not run/verified.
- **Promotion:** PR #89 remains draft and unmerged; exact-head test logs and reconciliation of the branch's two commits behind `main` are still required.
