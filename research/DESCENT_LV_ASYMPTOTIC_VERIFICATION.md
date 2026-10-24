# Descent LV — asymptotic verification note for the fixed-moment log envelope

**Status:** algebraic derivation plus deterministic regression checks. The result is restricted to the stated \(p,v\) path; it is not a universal asymptotic for arbitrary moment intervals.

## Setup

Use the canonical log-loss case \(a=1\), fixed mean \(p=\tfrac12\), fixed variance \(v=\tfrac1{20}\), and write
\[
\delta=1-b\downarrow0,\qquad b=1-\delta.
\]
The sharp fixed-moment witness from Descent LV is
\[
c_\delta=p-\frac{v}{b-p}
=\frac12-\frac{1/20}{1/2-\delta},
\qquad
\alpha_\delta=\frac{v}{(b-p)^2+v}
=\frac{1/20}{3/10-\delta+\delta^2}.
\]
The expected loss is
\[
U_\delta=(1-\alpha_\delta)\big[-\ln(1-c_\delta)\big]
+\alpha_\delta\ln\frac1\delta.
\]

## Exact limits and expansion

Taking \(\delta\to0^+\) gives
\[
c_\infty=\frac25=0.4,\qquad
\alpha_\infty=\frac16.
\]
Let \(L=-\ln(3/5)=-\ln 0.6\). Expanding the rational terms about \(\delta=0\),
\[
c_\delta=\frac25-\frac15\delta+O(\delta^2),
\qquad
\alpha_\delta=\frac16+\frac59\delta+O(\delta^2),
\]
and therefore
\[
-\ln(1-c_\delta)=L-\frac13\delta+O(\delta^2).
\]
Substitution yields
\[
\boxed{
U_\delta=
\frac16\ln\frac1\delta
+\frac56 L
+\frac59\delta\ln\frac1\delta
-\left(\frac59L+\frac5{18}\right)\delta
+O\!\left(\delta^2\ln\frac1\delta\right).
}
\]

There are two noninterchangeable statements:

1. The leading divergent coefficient is exactly \(1/6\):
   \[
   \frac{U_\delta}{(1/6)\ln(1/\delta)}\to1.
   \]
2. The **non-vanishing offset** is exactly
   \[
   C_\infty=\frac56[-\ln(0.6)]
   =0.42568801980499227\ldots
   \]
   Consequently, subtracting only the logarithmic leading term leaves a constant, not a vanishing remainder:
   \[
   U_\delta-\frac16\ln\frac1\delta\to C_\infty.
   \]
   After subtracting both leading term and constant, the residual is
   \[
   R_\delta=U_\delta-\frac16\ln\frac1\delta-C_\infty
   \sim\frac59\delta\ln\frac1\delta.
   \]
   It is \(O(\delta\log(1/\delta))\), not strictly \(O(\delta)\).

This resolves the apparent finite-sweep discrepancy: a ratio to only the leading logarithm approaches one slowly because the additive offset is positive. At \(\delta=10^{-4}\), direct calculation gives
\[
U_\delta=1.961200386616878,\quad
\frac16\ln(10^4)=1.535056728662697,
\]
\[
C_\infty=0.425688019804992,\quad
R_\delta=0.000455638149188,
\]
and
\[
\frac{U_\delta}{(1/6)\ln(1/\delta)}=1.2776077587\ldots
\]
not \(2.25\). The recording's \(2.25\) figure is not the ratio defined above under these canonical \(p,v\) assumptions; without its numerator and denominator it should not be reused as an asymptotic ratio. It may refer to a different quantity, but this note does not speculate which one.

## Great Scale map

| Quantity | Meaning |
|---|---|
| \(c_\infty=2/5\) | limiting interior witness atom |
| \(\alpha_\infty=1/6\) | limiting boundary atom probability; coefficient of the divergent logarithm |
| \(C_\infty=(5/6)(-\ln 0.6)\) | finite interior-atom contribution, retained after leading-term subtraction |
| \(R_\delta\) | second-order residual, with \(R_\delta\sim(5/9)\delta\ln(1/\delta)\) |
| SHARP_FIXED_MOMENT | exact fixed-\((p,v)\) envelope with its two-point witness |
| CHORD_FALLBACK | conservative bound for uncertain moments; not the sharp optimizer |

This asymptotic is a property of the fixed-moment family and the canonical \((p,v)=(1/2,1/20)\) path. It does not prove that a corner of an uncertain-moment rectangle maximizes the robust envelope. The feasible-set and proof-status requirements in the main Descent LV note remain in force.

## Reproduction

Run:
~~~bash
python3 test_descent.py
~~~
The asymptotic checks below are deterministic arithmetic regressions. The algebraic expansion is the proof; a finite delta sweep is supporting evidence, not a substitute.
