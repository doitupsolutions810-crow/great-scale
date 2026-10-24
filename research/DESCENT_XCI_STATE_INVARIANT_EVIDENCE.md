# Descent XCI — State, Invariants, and Evidence

Status: research synthesis and reproducibility protocol. The algebraic identities below are exact under the stated pure two-band assumptions. The independent numerical check is not a substitute for running the repository test suite.

## Finding

A scalar embedding is useful only if the information discarded by the embedding is explicitly identified. For the Great Scale topological channel, the scalar, signed topology, geometric magnitude, and numerical confidence are distinct fields.

For a gapped pure two-band model, with the conventions used in the existing QWZ implementation, define

\[
\mathcal A_Q=\frac{1}{2\pi}\int_{\mathrm{BZ}}|F_{12}|\,d^2k,\qquad
C=\frac{1}{2\pi}\int_{\mathrm{BZ}}F_{12}\,d^2k,\qquad
\eta_T=\frac{C}{\mathcal A_Q}.
\]

The triangle inequality gives \(|C|\leq\mathcal A_Q\), hence \(\eta_T\in[-1,1]\) whenever the area is positive and the integral is valid. The global Great Scale map is

\[
S_T=\frac{1-\eta_T^2}{4},\qquad
\Psi_T=\frac{3-\sqrt5}{2}+S_T.
\]

## Exact identities

Let

\[
P=\frac{1}{2\pi}\int\max(F_{12},0)\,d^2k,\qquad
N=\frac{1}{2\pi}\int\max(-F_{12},0)\,d^2k.
\]

Then \(C=P-N\), \(\mathcal A_Q=P+N\), and

\[
S_T=\frac{PN}{(P+N)^2},\qquad
\mathcal A_Q-|C|=2\min(P,N).
\]

With \(p_+=P/(P+N)\) and \(p_-=N/(P+N)\), the orientation entropy is

\[
H_T=-p_+\ln p_+-p_-\ln p_-.
\]

Because \(S_T=p_+p_-\) and entropy is determined by this binary distribution up to exchange of the two signs, entropy is an interpretable reparameterization, not an independent degree of freedom. It does not recover the sign of \(C\) or the absolute area. Preserve the tuple

\[
(\Psi_T,\eta_T,C,\mathcal A_Q,H_T,\text{validity},\text{convergence diagnostics}).
\]

## Identifiability and limits

1. The map is even in \(C\): replacing \(C\) by \(-C\) at equal area leaves \(S_T\), \(\Psi_T\), and binary entropy unchanged.
2. At \(C=0\) and positive area, \(\eta_T=0\), \(S_T=1/4\), and \(H_T=\ln 2\), independent of the absolute area.
3. A local pure-qubit QGT saturation identity does not determine the global Chern number. Global topology must be computed over the periodic parameter domain.
4. An integer-valued discrete Chern estimate does not certify convergence of the separate integral of \(|F_{12}|\). Grid refinement, grid-origin comparison, signed-curvature agreement, cancellation consistency, and entropy consistency are independent acceptance diagnostics.
5. A convergence heuristic is not a rigorous quadrature error bound. Results near gap-closing masses must remain unresolved unless the implemented validity checks pass.

## Reference-model verification protocol

For the Qi–Wu–Zhang Hamiltonian

\[
H_m(k_x,k_y)=\sin k_x\,\sigma_x+\sin k_y\,\sigma_y+
(m+\cos k_x+\cos k_y)\,\sigma_z,
\]

use the occupied lower band and the code's stated orientation convention.

Expected discrete Chern values:

| Mass | Expected C |
|---:|---:|
| \(m=-1\) | -1 |
| \(m=+1\) | +1 |
| \(m=3\) | 0 |

Reject transition masses \(m=-2,0,2\), even if a sampling grid would otherwise miss the gap-closing point. Verify the Chern number with the gauge-invariant Fukui–Hatsugai–Suzuki plaquette phase, independently compare the signed-curvature integral, and assess absolute-curvature/metric-area convergence across grid origins and refinements.

### Independent check recorded for this descent

A separate numerical implementation of the discrete plaquette calculation on a periodic 41×41 grid returned approximately -1, +1, and 0 for masses -1, +1, and 3, respectively. Floating-point deviations from the integers were at roundoff scale.

An independent algebraic property check over 10,000 nonnegative random pairs \((P,N)\) compared \((1-((P-N)/(P+N))^2)/4\) with \(PN/(P+N)^2\); maximum absolute discrepancy was approximately \(1.34\times10^{-16}\). This is an independent calculation, not evidence that the repository's own tests were executed.

## Required repository test run

From a clean checkout with dependencies installed:

```bash
npm test
python3 test_descent.py
npm run all
```

Record the commit SHA, runtime versions, exact command, exit status, and full test output before marking repository verification as passed. A passing algebraic micro-test must not be reported as a passing full repository test.

## Evidence registry record

- **Claim ID:** GS-DESCENT-XCI-STATE-INVARIANT
- **Source repository:** `doitupsolutions810-crow/great-scale`
- **Source branch for this research note:** `research/descent-xci-state-invariant-evidence`
- **Claim class:** exact algebraic identities plus model-specific numerical verification protocol
- **Assumptions:** gapped pure two-band model; stated curvature/Chern orientation; positive, converged metric-area integral
- **Independent check:** QWZ discrete plaquette values on 41×41 grid; 10,000-case algebraic identity check
- **Not yet established by this record:** full repository test-suite execution, rigorous quadrature error bound, or empirical physical law
- **Acceptance rule:** retain signed topology and geometric magnitude separately; reject or mark provisional any scalar mapping whose numerical validity gate fails
