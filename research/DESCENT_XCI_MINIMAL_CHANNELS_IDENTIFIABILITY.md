# Descent XCI — Minimal sufficient channels and identifiability audit

**Status:** exact algebraic result plus reproducible model-level checks. Not a new physical law or empirical claim.

## Repository analysis

The Great Scale scalar is intentionally lossy. The local QGT channel is
\[
S_Q=\frac14(1-\chi^2),\qquad \Psi_Q=\phi^{-2}+S_Q,
\quad \chi=\frac{|F_{12}|}{2\sqrt{\det g}}.
\]
The global two-band channel adds signed Chern number \(C\), metric-area budget \(\mathcal A_Q\), and signed polarization \(\eta=C/\mathcal A_Q\). The orientation-entropy descent then defines a binary entropy from the positive/negative curvature budgets. These are consistent layers, but they should not be mistaken for independent measurements.

## Finding: entropy adds interpretation, not information

Let \(P,N\ge0\) be the positive and negative curvature budgets, with \(\mathcal A_Q=P+N>0\) and \(C=P-N\). Then
\[
\eta=\frac{C}{\mathcal A_Q}=\frac{P-N}{P+N},\quad
p_+=\frac{1+\eta}{2},\quad p_-=\frac{1-\eta}{2}.
\]
The Great Scale correction is
\[
S_T=p_+p_- = \frac{1-\eta^2}{4},\qquad
\Psi_T=\phi^{-2}+S_T.
\]
Binary Shannon entropy is
\[
H_T=-p_+\ln p_+-p_-\ln p_-.
\]
Since \(S_T=p_+p_-\), the unordered probability pair is recovered from \(S_T\) as
\[
\{p_+,p_-\}=\left\{\frac{1-\sqrt{1-4S_T}}2,
\frac{1+\sqrt{1-4S_T}}2\right\}.
\]
Therefore \(H_T\) is exactly determined by \(S_T\): entropy is an interpretable reparameterization, not an additional independent degree of freedom. It cannot recover the sign of \(C\).

### Identifiability limits

1. **Opposite orientation:** \((C,\mathcal A_Q)\) and \((-C,\mathcal A_Q)\) have equal \(S_T,\Psi_T,H_T\). Preserve signed \(C\) or \(\eta\).
2. **Zero Chern number:** if \(C=0\), then \(\eta=0\), \(S_T=1/4\), and \(H_T=\ln2\), for every positive \(\mathcal A_Q\). The scalar and entropy cannot recover absolute area.
3. **Nonzero Chern number:** given valid \(S_T<1/4\) and known nonzero integer \(C\), \(\mathcal A_Q=|C|/\sqrt{1-4S_T}\) in exact arithmetic. This relies on the model assumptions and a converged area estimate.
4. **Local versus global:** local \(S_Q\) cannot stand in for global topology; the two-band local saturation identity may map topologically distinct phases to the same cone floor.

## Great Scale mapping

Keep the channels separate and label their information content:
- **Local shape/saturation:** \((\chi,S_Q,\Psi_Q)\)
- **Global signed topology:** \(C\)
- **Absolute geometric budget:** \(\mathcal A_Q\)
- **Signed normalized orientation:** \(\eta=C/\mathcal A_Q\)
- **Compact orientation-mixing scalar:** \(S_T=(1-\eta^2)/4\)
- **Entropy display:** \(H_T\), explicitly marked *derived from* \(S_T\)

Do not treat \(\Psi_T\), \(S_T\), and \(H_T\) as three independent evidence channels. The useful minimal tuple when orientation and scale matter is \((C,\mathcal A_Q)\), with the scalar and entropy retained as views/diagnostics.

## Test and verification protocol

Run `npm test`, `python3 test_descent.py`, and `python3 test_orientation_entropy.py`. The new Python checks cover: entropy invariance under \(\eta\mapsto-\eta\), exact reconstruction of the probability pair from \(S_T\), maximum entropy at \(C=0\), loss of area identifiability when \(C=0\), and area recovery when \(C\ne0\). These analytic checks do not replace grid-refinement, grid-origin, gap-closure rejection, or signed-curvature/Chern consistency checks in the numerical QWZ implementation.

## Reference interpretation

For the Qi–Wu–Zhang two-band model, the repository records \(C=-1\) at \(m=-1\), \(C=+1\) at \(m=+1\), and \(C=0\) at \(m=3\), using its stated orientation convention. The first two phases demonstrate orientation blindness of the even scalar; the zero-Chern phase demonstrates that maximal orientation entropy does not imply maximal geometric area.

**Conclusion:** the profound result is an identifiability boundary, not a new law. Great Scale can represent geometry, signed topology, normalized orientation mixing, and information-theoretic interpretation—but no single scalar can faithfully replace all four.
