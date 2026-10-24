# Descent LVII — Boundary asymptotic closure and witness accounting

**Status:** analytic consequence of the Descent LV/LVI fixed-moment envelope, with regression coverage. This is mathematics and software verification, not an empirical physical claim.

## Finding

For the supported negative-log loss
\[
f(P)=-a\ln(1-P),\qquad a>0,
\]
let \(P\in[0,b]\), \(b=1-\varepsilon\), and hold its mean \(p\) and variance \(v\) fixed as the boundary margin \(\varepsilon\downarrow0\). For each feasible pair, LV/LVI's sharp two-point extremizer is
\[
c_\varepsilon=p-\frac{v}{1-p-\varepsilon},\qquad
\alpha_\varepsilon=\frac{v}{(1-p-\varepsilon)^2+v},
\]
with probability \(\alpha_\varepsilon\) at the support boundary \(b=1-\varepsilon\), and probability \(1-\alpha_\varepsilon\) at \(c_\varepsilon\). Thus
\[
U_*(\varepsilon)
=(1-\alpha_\varepsilon)\big[-a\ln(1-c_\varepsilon)\big]
+\alpha_\varepsilon a\ln\frac1\varepsilon.
\]

Assume \(0<p<1\) and \(0\le v<p(1-p)\), so the fixed moment pair remains feasible for all sufficiently small positive \(\varepsilon\). Put
\[
c_0=p-\frac{v}{1-p},\qquad
\alpha_0=\frac{v}{(1-p)^2+v}.
\]
Then \(c_\varepsilon=c_0+O(\varepsilon)\) and \(\alpha_\varepsilon=\alpha_0+O(\varepsilon)\), giving the boundary asymptotic
\[
\boxed{
U_*(\varepsilon)
=a\alpha_0\ln\frac1\varepsilon
+a(1-\alpha_0)\big[-\ln(1-c_0)\big]
+O\!\left(\varepsilon\ln\frac1\varepsilon\right).
}
\]

**Interpretation:** the coefficient of the logarithmic divergence is the limiting probability mass of the extremizer placed on the singular boundary. The finite constant is the loss contribution of the interior atom. A single reported risk number hides this decomposition; the witness reveals it.


## General boundary-singularity closure for LVI's power barrier

The leading-coefficient result is not specific to the logarithm. The same witness parameters satisfy
\[
\alpha_\varepsilon=\alpha_0+O(\varepsilon),\qquad c_\varepsilon=c_0+O(\varepsilon).
\]
For any supported loss whose value and derivative remain finite near \(c_0\), this gives
\[
U_f^*(\varepsilon)
=\alpha_0 f(1-\varepsilon)+(1-\alpha_0)f(c_0)
+O\!\left(\varepsilon |f(1-\varepsilon)|+\varepsilon\right).
\]
Consequently, for LVI's power-barrier family
\[
f_{\rm barrier}(P)=a\big[(1-P)^{-r}-1\big],\qquad a>0,\ r>0,
\]
and \(v>0\) (so \(\alpha_0>0\)),
\[
U_{\rm barrier}^*(\varepsilon)
=a\alpha_0\varepsilon^{-r}+O(\varepsilon^{1-r}+1),
\qquad
\frac{U_{\rm barrier}^*(\varepsilon)}{a\varepsilon^{-r}}\longrightarrow\alpha_0.
\]
Unlike the logarithmic case, for \(r\geq1\) the subleading correction can itself diverge; it is not generally correct to declare the finite interior contribution the entire constant remainder after only subtracting the leading power.

The degenerate case \(v=0\) is important: the witness is the point mass at \(p\), \(\alpha_\varepsilon=0\) exactly, and \(U_f^*(\varepsilon)=f(p)\) stays finite as \(\varepsilon\downarrow0\). Thus a singular loss does not automatically produce a divergent envelope; the extremal witness must place nonzero probability at the singular boundary.

## Explicit expansion for the repository's regression case

For \(p=\frac12\), \(v=0.05\), \(a=1\):
\[
c_0=0.4,\qquad \alpha_0=\frac16,
\]
so
\[
U_*(\varepsilon)
=\frac16\ln\frac1\varepsilon
+\frac56\ln\frac53
+O\!\left(\varepsilon\ln\frac1\varepsilon\right).
\]
Expanding one order further gives
\[
\boxed{
\begin{aligned}
U_*(\varepsilon)
={}&\frac16\ln\frac1\varepsilon
+\frac56\ln\frac53\\
&+\frac59\varepsilon\ln\frac1\varepsilon
-\left(\frac5{18}+\frac59\ln\frac53\right)\varepsilon\\
&+O\!\left(\varepsilon^2\ln\frac1\varepsilon\right).
\end{aligned}
}
\]
The coefficients follow from
\[
\alpha_\varepsilon=\frac16+\frac59\varepsilon+O(\varepsilon^2),\qquad
c_\varepsilon=\frac25-\frac15\varepsilon+O(\varepsilon^2).
\]
This resolves the apparent blow-up at \(x=1\): the expected loss does diverge as the support approaches the singularity, but its leading coefficient and finite remainder are derivable from the extremal witness. One must not evaluate the loss at \(P=1\); the support margin is strictly positive throughout the limit.

## What this adds to LV and LVI

- **LV:** a sharp fixed-moment Hermite-majorant bound does not prove that an uncertain-moment robust maximum is at the upper-right corner. The maximum must be certified over the full feasible set; otherwise report the conservative chord fallback.
- **LVI:** for the negative-log and power-barrier families, the positive third derivative justifies the quadratic Hermite majorant and the fixed-moment two-point witness. The global uncertain-moment maximum remains separately uncertified unless its optimization is proved.
- **LVII:** the boundary margin is not just an input-validity switch. It controls the divergence rate of the sharp loss envelope, and that rate equals the boundary atom's limiting probability. The constant term retains the interior atom's contribution.

The first two results are about the extremal value and how it is certified; this descent makes the singular-limit behavior of that value explicit and testable.

## Great Scale mapping

The risk envelope is an additional typed channel; it does not replace Great Scale's existing state law:
\[
S(h)=h(1-h),\qquad
\Psi=\phi^{-2}+S,\qquad
\Psi\ge\phi^{-2}\approx0.381966.
\]
A risk certificate should travel as a tuple, not a bare scalar:
\[
\mathcal C=(U,\mathcal F,\varepsilon,W,\mathsf{method},\mathsf{status}),
\]
where \(U\) is the reported bound, \(\mathcal F\) is the feasible moment set, \(\varepsilon\) is the support margin, \(W\) is the two-point witness, and method/status distinguish a proved fixed-moment extremum, a certified analytic fallback, and an uncertified robust-global maximum.

This is the same projection discipline being integrated into CycleKernel: its score \(N=\sqrt{s n}\) is non-injective, so the raw symbolic/neural channels, source metadata, decision margins, and state witness must remain alongside the scalar. The linked CycleKernel [GS–LVI evidence PR](https://github.com/doitupsolutions810-crow/CycleKernal/pull/9) carries that proposal but remains open/draft; its source and CI status must not be represented as merged or production-verified.


## Cross-repository descent: missingness is part of the observation state

A second non-injective projection appears in CycleKernel's evidence pipeline. Python truthiness mapped both an absent mapping and an explicitly empty mapping to the same default. Great Scale's typed-certificate rule implies those inputs must remain distinguishable: input presence, effective values, and source labels belong in the witness.

The integrated CycleKernel branch now distinguishes:
\[
\operatorname{Absent}\mapsto\text{documented baseline},\qquad
\operatorname{Present}(\{\})\mapsto\text{explicit empty input}.
\]
For the current symbolic formula, the baseline score is \(0.4325\), while the explicit empty-resource score is \(0.275\). The resulting state fingerprints differ, and the evidence witness is checked against the reported fingerprint. This is not a change to Great Scale's heat law; it is a shared rule for preserving conditions that a scalar otherwise discards.

Field-level presence is now preserved too: an omitted field and an explicitly supplied zero remain distinct in the canonical witness, and validated belief.deception is recorded even though the existing score does not use it. See [CycleKernel Descent C — Typed missingness](https://github.com/doitupsolutions810-crow/CycleKernal/blob/feature/gs-lvi-closed-loop-evidence/docs/DESCENT_C_TYPED_MISSINGNESS.md), [Descent CI — Field-presence closure](https://github.com/doitupsolutions810-crow/CycleKernal/blob/feature/gs-lvi-closed-loop-evidence/docs/DESCENT_CI_WITNESS_COMPLETENESS.md), and the open [GS–LVI integration PR #9](https://github.com/doitupsolutions810-crow/CycleKernal/pull/9). These source changes are under review and are not yet merge- or production-verified.

## Regression criteria

The new test in test_loss_envelope.py:
1. reproduces the limiting boundary mass \(1/6\) and interior point \(0.4\);
2. subtracts the leading logarithm and finite constant and verifies the remainder shrinks as the support margin decreases;
3. verifies the first-order correction and its \(O(\varepsilon^2\ln(1/\varepsilon))\) remainder over a deterministic epsilon sweep;
4. verifies that the power-barrier envelope normalized by \(a\varepsilon^{-r}\) converges to the extremal boundary mass, while the zero-variance case remains finite;
5. leaves the existing fixed-moment and chord-fallback tests intact.

Run the branch's existing checks:
~~~bash
npm run build
npm test
python3 test_descent.py
python3 test_loss_envelope.py
npm run all
~~~

The test implementation is added to the existing LVI suite. Hosted CI had previously reported failure before runner allocation, with empty step lists; that is not a test pass or a test assertion failure. Until an Actions job executes real steps on this head, repository-wide runtime verification remains pending.

## Scientific boundary

The Hermite remainder and the asymptotic expansion are mathematical claims about the specified loss and support/moment assumptions. They do not establish empirical calibration of a risk model, prove that a real-world distribution obeys the assumed moments, or authorize an operational decision. The support margin and proof status must be visible at the point where the scalar is consumed.


## Cross-repository continuation: explicit-null closure (CycleKernel Descent CII)

The same typed-observation principle catches a further ambiguity below the empty-mapping fix. In Python, `metrics.get(k)` maps both an omitted key and a supplied `null`/`None` to the same value. The CycleKernel backend and both maintained bridge fusion copies now treat omission as absent/defaulted, preserve supplied mappings (including empty mappings), and reject a supplied null/non-mapping value. This does not alter the Great Scale heat/cone law or CycleKernel's fitness formula; it makes malformed input fail closed. See [Descent CII](https://github.com/doitupsolutions810-crow/CycleKernal/blob/feature/gs-lvi-closed-loop-evidence/docs/DESCENT_CII_EXPLICIT_NULL_CLOSURE.md) and [GS–LVI PR #9](https://github.com/doitupsolutions810-crow/CycleKernal/pull/9). As before, source integration and test additions are not equivalent to a passing hosted build.
