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


## Descent LXXIX — Sign-consistent curvature and a topological metric-area bound

### Finding 1: the occupied-band curvature sign must agree with the global invariant

The lower-band projector of this Hamiltonian has Bloch vector \(s(k)=-d(k)/|d(k)|\), not \(+d/|d|\). Replacing \(n\) by \(-n\) leaves the quantum metric unchanged but reverses the Berry-curvature sign. Therefore the analytic lower-band curvature must be
\[
F_{12}=-\frac12 n\cdot(\partial_{k_x}n\times\partial_{k_y}n),
\quad n=d/|d|.
\]
The old sign did not affect the absolute-curvature Great Scale scalar, but it disagreed with the Fukui–Hatsugai–Suzuki (FHS) Chern-number orientation. The analytic routine is corrected, and a new test compares the full-zone curvature integral with the independently link-computed Chern number for \(m=\pm1\).

### Finding 2: quantum-metric area pays a topological minimum

For a pure two-band state,
\[
\det g=\frac{F_{12}^{2}}4,\qquad
\sqrt{\det g}=\frac{|F_{12}|}{2}.
\]
Define the dimensionless metric-area budget on the Brillouin torus:
\[
\mathcal A_Q=\frac1\pi\int_{\mathrm{BZ}}\sqrt{\det g}\,d^2k
=\frac1{2\pi}\int_{\mathrm{BZ}}|F_{12}|\,d^2k.
\]
Because the Chern number is the signed curvature integral, the triangle inequality gives
\[
\boxed{\mathcal A_Q\ge |C|},\qquad
\mathcal E_Q=\mathcal A_Q-|C|\ge0.
\]
This separates net topological degree from unsigned geometric coverage: positive and negative local curvature can cancel in \(C\), but both contribute to metric area. The excess \(\mathcal E_Q\) measures area beyond the minimum forced by topology.

### Great Scale mapping

Keep the established local scalar unchanged:
\[
\Psi_Q=\phi^{-2}+S_Q,\quad S_Q=\frac14(1-\chi^2).
\]
Expose a separate global channel with \(C\in\mathbb Z\), \(\mathcal A_Q\), and \(\mathcal E_Q\). For a compact Great Scale scalar, define the topological saturation ratio \(\tau=|C|/\mathcal A_Q\in[0,1]\), then
\[
h_T=\frac{1+\tau}{2},\quad
S_T=h_T(1-h_T)=\frac{1-\tau^2}{4},\quad
\Psi_T=\phi^{-2}+S_T.
\]
The implementation emits chernNumber, metricAreaBudget, metricAreaExcess, topologicalSaturation, STopological, and psiTopological. Preserve the signed integer \(C\) separately: the heat scalar intentionally loses its sign. This is an additive diagnostic, not a replacement for the phase-driven Great Scale state or a physical law.

### Verification added

Tests check (1) local curvature integration agrees in sign and value with the FHS Chern result in both \(C=\pm1\) phases, (2) \(\mathcal A_Q=\frac1{2\pi}\int|F|\ge|C|\), (3) the metric-area budget approaches a stable value from 40×40 to 80×80, and (4) the trivial phase has \(C=0\) despite a nonzero unsigned metric-area budget. The lower bound follows analytically from the QGT identity and triangle inequality; the numerical tests verify its implementation for this Hamiltonian.


## Descent LXXX — Numerical certification across the phase diagram

A discrete Chern estimate and a quadrature of the analytic Berry curvature are related but distinct numerical procedures. The FHS lattice-link sum is gauge-invariant and is the primary integer diagnostic; the local-curvature integral is a separate numerical quadrature that should be validated by refinement rather than forced to equal the integer at arbitrary precision on one grid.

For the Qi–Wu–Zhang model, the gapped phases represented by the sweep are:
- (m<-2): (C=0)
- (-2<m<0): (C=-1) with this code's orientation
- (0<m<2): (C=+1)
- (m>2): (C=0)

The exact transition masses (m=-2,0,2) remain rejected. The added sweep samples multiple parameter values in each gapped region, requiring the FHS result to be close to an integer and to match the expected phase. A separate refinement check compares 40×40 and 80×80 curvature quadrature error. This is a numerical reliability improvement for this Hamiltonian, not a universal grid-size guarantee; points close to a transition may require much finer sampling.
