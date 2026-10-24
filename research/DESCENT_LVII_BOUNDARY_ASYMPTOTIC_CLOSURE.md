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

## Regression criteria

The new test in test_loss_envelope.py:
1. reproduces the limiting boundary mass \(1/6\) and interior point \(0.4\);
2. subtracts the leading logarithm and finite constant and verifies the remainder shrinks as the support margin decreases;
3. verifies the first-order correction and its \(O(\varepsilon^2\ln(1/\varepsilon))\) remainder over a deterministic epsilon sweep;
4. leaves the existing fixed-moment and chord-fallback tests intact.

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
