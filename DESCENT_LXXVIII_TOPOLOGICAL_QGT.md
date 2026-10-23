# Descent LXXVIII — Local QGT saturation does not determine global topology

Status: reproducible mathematical/model result. This is not a new physical law or experimental claim.

## Model

Use the two-band Qi–Wu–Zhang lattice Hamiltonian on the Brillouin torus:
\[
H_m(k_x,k_y)=\sin k_x\,\sigma_x+\sin k_y\,\sigma_y+
(m+\cos k_x+\cos k_y)\,\sigma_z.
\]
The occupied state is the lower-energy eigenstate. The band gap closes at the phase boundaries \(m=-2,0,2\). With the orientation used in the implementation, the discrete Chern numbers are \(C=-1\) for \(m=-1\), \(C=+1\) for \(m=+1\), and \(C=0\) for \(m=3\).

## Why the local Great Scale channel misses this distinction

For a pure two-level state, write the Bloch vector \(n=d/|d|\). At a regular point,
\[
g_{ij}=\frac14\,\partial_i n\cdot\partial_j n,\qquad
|F_{12}|=\frac12\left|n\cdot(\partial_1 n\times\partial_2 n)\right|.
\]
Because \(\partial_i n\) lie in the two-dimensional tangent plane of the unit sphere,
\[
\det g=\frac{F_{12}^2}{4},\qquad
\chi=\frac{|F_{12}|}{2\sqrt{\det g}}=1.
\]
Thus the existing local bridge gives \(S_Q=0\) and \(\Psi_Q=\phi^{-2}\) at every regular point of any such pure two-band map, including topologically distinct phases. This is a local saturation identity; it does not say the band is gapless or topologically trivial.

The Chern number is a global invariant. On the periodic grid, the test uses normalized neighbor overlaps \(U_\mu(k)=\langle u(k)|u(k+\hat\mu)\rangle/|\langle u(k)|u(k+\hat\mu)\rangle|\), then sums the gauge-invariant plaquette phases:
\[
C_N=\frac{1}{2\pi}\sum_k \arg\!\left[
U_x(k)U_y(k+\hat x)U_x(k+\hat y)^*U_y(k)^*
\right].
\]
The chosen orientation fixes the reported signs; reversing orientation reverses \(C\), while the distinction between \(C=-1,+1,0\) remains.

## Great Scale mapping

Keep the established local scalar channel:
\[
S_Q=\frac14\left(1-\chi^2\right),\qquad
\Psi_Q=\phi^{-2}+S_Q.
\]
Add a separate global channel \(C\in\mathbb Z\), computed over the complete periodic parameter domain. Do not try to reconstruct \(C\) from \(S_Q\), \(\chi\), or a single local metric-curvature sample. Signed local curvature is useful diagnostics but is not, by itself, a substitute for integrating curvature over the full closed manifold.

## Verification

Run `npm test`. The added tests check:
1. \(C=-1\) for \(m=-1\), \(C=+1\) for \(m=+1\), and \(C=0\) for \(m=3\).
2. The critical masses \(m=-2,0,2\) are rejected even on an odd-sized grid, so a sampling grid cannot hide the known gap closure.
3. The analytic local QGT of both \(m=-1\) and \(m=+1\) maps to the same Great Scale cone floor.

The Chern calculation uses the Fukui–Hatsugai–Suzuki discrete plaquette formula. The test is numerical verification for this specified model and grid, not a general proof of all topological systems.
