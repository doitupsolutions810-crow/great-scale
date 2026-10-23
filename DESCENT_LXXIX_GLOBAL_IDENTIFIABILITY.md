# Descent LXXIX — Local saturation requires a global identifiability certificate

Status: mathematical consequence of the Great Scale QGT bridge and the two-band QWZ test model. No claim of a new physical law. This document extends LXXVIII with an explicit contract for when the local scalar and global topological channels may be interpreted together.

## Finding

For a regular pure two-level state map with Bloch vector \(n(k_x,k_y)\), the local quantum geometric tensor obeys

\[
g_{ij}=\tfrac14\,\partial_i n\cdot\partial_j n,\qquad
F_{12}=\tfrac12 n\cdot(\partial_1n\times\partial_2n).
\]

At a regular point, both derivatives lie in the tangent plane to \(S^2\), so

\[
\det g=F_{12}^2/4,\qquad \chi=|F_{12}|/(2\sqrt{\det g})=1.
\]

Consequently the existing scalar bridge returns \(S_Q=(1-\chi^2)/4=0\) and \(\Psi_Q=\phi^{-2}\) throughout regular patches, even when the complete maps have different Chern numbers. The local scalar is therefore not a sufficient statistic for global topology.

The global invariant for a smooth, gapped two-band map is its degree:

\[
C=\frac{1}{4\pi}\int_{T^2}
n\cdot(\partial_{k_x}n\times\partial_{k_y}n)\,d^2k\in\mathbb Z.
\]

For the repository's QWZ model, the documented orientation gives \(C=-1\) at \(m=-1\), \(C=+1\) at \(m=+1\), and \(C=0\) at \(m=3\), while the local QGT scalar saturates to the same cone floor in both nontrivial phases.

## Great Scale mapping

Keep these as distinct state coordinates rather than forcing them into one scalar:

- Local geometry: \(S_Q\in[0,1/4]\), \(\Psi_Q=\phi^{-2}+S_Q\).
- Global topology: integer \(C\), computed over the complete periodic domain.
- Numerical confidence: a separate admissibility record containing minimum sampled band gap, minimum neighbor-overlap magnitude, grid size, and agreement under grid refinement.

No value of \(S_Q\) alone determines \(C\). A claim about \(C\) must identify the Hamiltonian/model, orientation convention, periodic domain, discretization, and gap/overlap checks.

## Numerical contract to test

1. **Gap gate:** reject known phase-boundary masses \(m\in\{-2,0,2\}\), and more generally reject a model when its gap falls below an explicitly configured tolerance. The tolerance is a numerical policy, not a universal physical constant.
2. **Overlap gate:** reject a plaquette calculation if any neighbor overlap used for normalization is zero or below a documented tolerance; otherwise the normalized link phase is ill-conditioned.
3. **Refinement gate:** compute on at least two grid sizes and report whether the integer result agrees. Agreement is evidence of numerical stability for those grids, not a proof of convergence for every model.
4. **Scalar/topology separation:** demonstrate that \(m=-1\) and \(m=+1\) have the same local \(\Psi_Q\) at regular points but opposite \(C\).
5. **Orientation check:** reverse one coordinate orientation and verify that \(C\) changes sign while \(|C|\) and the local scalar remain unchanged.
6. **Reproducibility record:** persist model parameters, grid size, gap diagnostics, overlap diagnostics, algorithm name, orientation, computed integer, and test result together.

## Interpretation

This is an identifiability boundary, not a contradiction: the local map deliberately compresses information. A robust platform should preserve the compression where it is useful, while refusing to treat its output as evidence for information it discarded. The same design rule applies to other system layers: a single scalar health score must not stand in for provenance, completeness, or global consistency.

## Evidence ledger

- Source-grounded: repository documentation and tests define the local QGT mapping and QWZ Chern computation.
- Analytic: local saturation follows from the two-dimensional tangent-plane identity; the degree integral is global.
- Existing documented test coverage: Chern values at three masses, phase-boundary rejection, opposite phases sharing the scalar floor, and 20x20 versus 40x40 agreement.
- Not yet executed in this session: full npm test suite, Python descent suite, live deployment test, and additional orientation/gap-tolerance experiments. A remote source read is not a runtime test.
