# Descent LV — Robust risk certificates with uncertain moments and boundary margin

**Status:** research result / review required; not a production guarantee.  
**Scope:** mathematical certificate for \(f(P)=-a\ln(1-P)\), \(a>0\). This document does not claim an empirical law or that a repository test suite was run.

## Finding

A fixed-moment extremal theorem does not justify selecting the upper-right corner of an uncertainty rectangle without an additional monotonicity proof. Convexity of \(f\) alone is not that proof. The robust certificate is the maximum of the fixed-moment sharp envelope over the *whole feasible uncertainty set*. A simpler closed-form chord bound is always available and avoids an unjustified corner assumption.

This distinction is the central Descent LV result: **robustness is an optimization over the admissible set, not a visual choice of its corner.**

## Assumptions and feasible set

Let \(P\) be a random variable with
\[
0\le P\le b:=1-\varepsilon_L<1,\qquad a>0,\qquad \varepsilon_L>0.
\]
Suppose its mean and variance are constrained by
\[
p\in[p_L,p_U],\qquad v\in[v_L,v_U].
\]
The feasible moment set is
\[
\mathcal F=\{(p,v):p_L\le p\le p_U,\ v_L\le v\le v_U,\
0\le p\le b,\ 0\le v\le p(b-p)\}.
\]
The last inequality is necessary for any distribution supported on \([0,b]\), since \(P^2\le bP\), so
\[
v=\mathbb E[P^2]-p^2\le bp-p^2=p(b-p).
\]
It is not sufficient to specify interval endpoints that make \(\mathcal F\) empty; implementation must detect infeasibility and return INVALID_INPUT, not a risk number.

## Fixed-moment sharp envelope

For \(0\le p<b\) and \(0\le v\le p(b-p)\), define
\[
c=p-\frac{v}{b-p},\qquad
\alpha=\frac{v}{(b-p)^2+v}.
\]
Then \(c\in[0,p]\), \(\alpha\in[0,1)\), and the two-point law
\[
\Pr(P=b)=\alpha,\qquad \Pr(P=c)=1-\alpha
\]
has mean \(p\) and variance \(v\). Its expected loss is
\[
U_*(p,v;b)=(1-\alpha)f(c)+\alpha f(b).
\]
For \(v=0\), interpret the law as the degenerate distribution at \(p\), so \(U_*=f(p)\). At the edge \(p=b\), feasibility forces \(v=0\) and again \(U_*=f(b)\).

**Why this is sharp.** For \(v>0\) and \(p<b\), let \(q\) be the quadratic Hermite interpolant satisfying
\(q(c)=f(c)\), \(q'(c)=f'(c)\), and \(q(b)=f(b)\).
Since
\[
f'''(x)=\frac{2a}{(1-x)^3}>0,
\]
the Hermite remainder gives, for \(x\in[0,b]\),
\[
f(x)-q(x)=\frac{f'''(\xi_x)}{3!}(x-c)^2(x-b)\le0
\]
(with the usual limiting interpretation at interpolation nodes). Thus \(f\le q\). Because \(q\) is quadratic, \(\mathbb E[q(P)]\) depends only on the first two moments; it equals the expectation under the two-point law above, where \(q=f\) at both support points. Hence every distribution with these fixed moments has \(\mathbb E[f(P)]\le U_*(p,v;b)\), and the two-point law attains equality.

## Robust certificate for uncertain moments

The sharp robust value is
\[
\boxed{U_{\mathrm{rob}}=
\max_{(p,v)\in\mathcal F} U_*(p,v;b).}
\]
Because \(b<1\), the loss is bounded and continuous on \([0,b]\); the admissible distribution family is weakly compact, and the supremum is finite and attained whenever \(\mathcal F\ne\varnothing\). The formula above is exact, but **it does not imply that the maximizer is \((p_U,v_U)\)**. The maximizing moment pair must be established by a separate monotonicity proof or by a verified global optimization over \(\mathcal F\). A local optimizer or a grid scan alone is not a proof of global sharpness.

If the implementation cannot certify a global maximum, it must label its numerical result ESTIMATE, not SHARP_CERTIFICATE. A safe analytic fallback is the chord bound below.

## A simple, rigorous fallback bound

For \(x\in[0,b]\), convexity gives the chord inequality
\[
f(x)\le \frac{x}{b}f(b)
\quad (b>0).
\]
Taking expectations and using \(p\le p_U\),
\[
\boxed{\mathbb E[f(P)]\le
\frac{a\,p_U}{1-\varepsilon_L}\ln\frac1{\varepsilon_L}.}
\]
If \(b=0\), then \(P=0\) almost surely and the risk is zero. The fallback is conservative but requires no variance estimate and no corner-monotonicity assumption. Clamp no inputs silently; reject invalid ranges explicitly.

## Numerical audit of the illustrative case

For \(a=1\), \(b=0.95\), \(p=0.50\), and \(v=0.05\):
\[
c=0.50-\frac{0.05}{0.95-0.50}=0.388888\ldots,
\qquad
\alpha=\frac{0.05}{0.45^2+0.05}=0.1980198\ldots
\]
The two-point expected loss is
\[
U_*\approx 0.9881707006.
\]
The chord bound is
\[
U_{\mathrm{chord}}=\frac{0.50}{0.95}\ln(20)
\approx1.5767011966.
\]
Thus the sharp fixed-moment value is below the chord bound, as required. Any report giving approximately \(0.784\) for this same example is arithmetically incorrect and must not be copied into the canonical Great Scale state.

## Great Scale mapping

| Element | Descent LV encoding |
|---|---|
| Mean axis | Explicit interval \([p_L,p_U]\) |
| Variance axis | Explicit interval \([v_L,v_U]\), intersected with \(v\le p(b-p)\) |
| Boundary axis | Guaranteed \(\varepsilon_L>0\), with support cap \(b=1-\varepsilon_L\) |
| Feasibility gate | \(\mathcal F\ne\varnothing\); otherwise INVALID_INPUT |
| Sharp risk surface | \(U_{\mathrm{rob}}=\max_{\mathcal F}U_*(p,v;b)\), only when global maximization is certified |
| Safe fallback | \(U_{\mathrm{chord}}=a p_U\ln(1/\varepsilon_L)/(1-\varepsilon_L)\), after validating \(p_U\) and support assumptions |
| Witness | Extremal two-point law for the maximizing feasible pair |
| Invalidation event | Margin guarantee, moment intervals, or support assumptions violated |
| Promotion state | Proposed; do not label production-certified until code and CI verify the implementation |

The UI should display the intervals, the support cap, the feasible-set status, the method (SHARP_GLOBAL versus CHORD_FALLBACK), and the proof/verification status together. A scalar without its assumptions is not a risk certificate.

## Required verification plan

These are **test specifications, not claimed test results**:

1. **Input validation:** reject \(\varepsilon_L\le0\), \(p_L>p_U\), \(v_L>v_U\), negative variance, or empty \(\mathcal F\).
2. **Moment reconstruction:** for random feasible \((p,v)\), construct the two-point law and verify normalization, mean, and variance within numerical tolerance.
3. **Sharpness witness:** evaluate the loss of the constructed law and compare it to \(U_*\).
4. **Majorant check:** densely sample \(x\in[0,b]\) and check \(f(x)\le q(x)+\tau\); this is a numerical diagnostic, not a substitute for the proof.
5. **Bound dominance:** verify \(U_*(p,v;b)\le U_{\mathrm{chord}}(p;b)\) over seeded feasible samples.
6. **Robust optimizer:** compare any proposed global optimizer with exhaustive fine-grid and boundary searches on test fixtures; require a certified optimizer or use the chord fallback.
7. **Boundary cases:** \(v=0\), \(p=0\), \(p=b,v=0\), \(v=p(b-p)\), very small positive \(\varepsilon_L\), and intervals touching feasibility boundaries.
8. **Regression:** run npm test, python3 test_descent.py, and npm run all in the Great Scale repository; retain logs and commit SHA.

## Verification state and integration decision

Repository conventions observed in great-scale include the research Markdown files, npm test, python3 test_descent.py, and npm run all. This document is a research proposal; it does not modify runtime behavior. No local execution result is asserted here. Before promotion, implement the helper and tests, run the commands above in CI, review the numerical global-optimization method, and retain the CI result.

The existing objective-sign inconsistency and controller behavior noted in earlier descents are outside this proof and remain separate release gates.

## Literature context

The chord fallback is the classical convex-function chord bound associated with Edmundson–Madansky. The sharp fixed-moment construction is a moment-problem/Hermite-majorant argument. These are established mathematical techniques; the Great Scale contribution here is the explicit treatment of the uncertainty set, feasibility gate, and status-aware certificate contract—not a claim of a new physical law.


## Asymptotic verification addendum

The fixed-moment log-loss path \(p=1/2, v=1/20, b=1-\delta\) has exact limits \(c_\infty=2/5\), \(\alpha_\infty=1/6\), and finite offset \(C_\infty=(5/6)[-\ln(0.6)]\). The residual after subtracting both the leading logarithm and this offset is asymptotic to \((5/9)\delta\ln(1/\delta)\). See [DESCENT_LV_ASYMPTOTIC_VERIFICATION.md](DESCENT_LV_ASYMPTOTIC_VERIFICATION.md). A reported finite-sweep ratio of 2.25 is not \(U_\delta/[(1/6)\ln(1/\delta)]\) for the canonical assumptions; at \(\delta=10^{-4}\), the latter is approximately 1.277608. Do not carry the 2.25 value forward without the ratio's exact definition.
