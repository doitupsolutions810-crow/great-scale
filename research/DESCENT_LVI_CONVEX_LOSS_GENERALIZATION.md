# Descent LVI — Convex barrier-loss generalization with proof labels

**Status:** analytic extension and implementation proposal. No new physical law, empirical result, or unexecuted CI pass is claimed.

## Profound finding

The reusable condition behind Descent LV is not merely convexity. It is the sign of the third derivative on the supported interval.

For a loss \(f\in C^3([0,b])\) with \(f'''(x)\ge0\), the quadratic Hermite interpolant with a double node at the lower support point \(c\) and a single node at the upper support endpoint \(b\) is a pointwise majorant. Its expectation depends only on the first two moments, which makes a particular two-point distribution a sharp fixed-moment extremizer.

Descent LVI makes that condition explicit for two supported, diverging-curvature families:

1. **Scaled negative logarithm**
   \[
   f_{\log}(x)=-a\ln(1-x),\qquad a>0,
   \]
   \[
   f'''_{\log}(x)=\frac{2a}{(1-x)^3}>0.
   \]

2. **Power barrier**
   \[
   f_{\mathrm{barrier}}(x)=a\big[(1-x)^{-r}-1\big],
   \qquad a>0,\ r>0,
   \]
   \[
   f'''_{\mathrm{barrier}}(x)
   =ar(r+1)(r+2)(1-x)^{-r-3}>0.
   \]

Both satisfy \(f(0)=0\), are increasing and convex, and diverge as \(x\to1^{-}\). The support margin \(\varepsilon_L>0\) keeps \(b=1-\varepsilon_L\) strictly below the singularity.

## Fixed-moment sharp envelope

Let \(P\in[0,b]\) with mean \(p\) and variance \(v\). Feasibility requires
\[
0\le p\le b,\qquad 0\le v\le p(b-p).
\]
For \(p<b\), define
\[
c=p-\frac{v}{b-p},\qquad
\alpha=\frac{v}{(b-p)^2+v}.
\]
The witness distribution is
\[
\Pr(P=b)=\alpha,\qquad \Pr(P=c)=1-\alpha.
\]
It has exactly the prescribed mean and variance. For \(v=0\), use the point mass at \(p\); for \(p=b\), feasibility forces \(v=0\).

Let \(q\) be the unique quadratic satisfying \(q(c)=f(c)\), \(q'(c)=f'(c)\), and \(q(b)=f(b)\). The Hermite remainder is
\[
f(x)-q(x)=\frac{f'''(\xi_x)}{3!}(x-c)^2(x-b)\le0
\quad (0\le x\le b).
\]
Thus \(f(x)\le q(x)\) over the whole support. Since \(q\) is quadratic, \(\mathbb E[q(P)]\) depends only on \(p\) and \(v\). The witness places mass only where \(q=f\), so its loss attains the bound:
\[
\boxed{
U_f^*(p,v;b)=(1-\alpha)f(c)+\alpha f(b).
}
\]
This is a **sharp fixed-moment** result for these two families. In the implementation module loss_envelope.py, the returned status is PROVED_FIXED_MOMENT; the witness moments and a positive lower bound for \(f'''\) are emitted for audit.

## Uncertain moments: do not invent a sharp optimizer

When \(p\) and \(v\) are only known to lie in intervals, the exact robust envelope remains
\[
U_{\mathrm{rob}}
=\max_{(p,v)\in\mathcal F}U_f^*(p,v;b),
\]
where
\[
\mathcal F=\{(p,v):p_L\le p\le p_U,\ v_L\le v\le v_U,\
0\le p\le b,\ 0\le v\le p(b-p)\}.
\]
The fixed-moment theorem does **not** prove the maximizer is the upper-right corner of the rectangle. Convexity or a grid search alone is not a global-maximizer certificate.

The implementation therefore offers a separately labelled conservative fallback. Since both supported losses are convex with \(f(0)=0\),
\[
f(x)\le\frac{x}{b}f(b),\qquad 0\le x\le b,\ b>0.
\]
Hence
\[
\boxed{
\mathbb E[f(P)]
\le \frac{p_{\max,\mathcal F}}{b}f(b),
}
\]
where \(p_{\max,\mathcal F}\) is computed after intersecting the supplied moment box with the support and the necessary \(v_L\le p(b-p)\) constraint. For \(b=0\), feasible support is \(\{0\}\) and risk is zero.

The output is labelled CHORD_FALLBACK / CERTIFIED_ANALYTIC_BOUND; robust_global_status remains NOT_CERTIFIED. An empty feasible set raises an error rather than returning a risk value. This is deliberate: a safe bound is preferable to an unjustified sharp label.

## Mapping to the Great Scale

Great Scale's current state remains unchanged:
\[
S(h)=h(1-h),\qquad
\Psi=\phi^{-2}+S,\quad
\Psi\ge\phi^{-2}\approx0.381966.
\]
The loss-envelope result is an **additional typed risk channel**, not a redefinition of \(S\) or \(\Psi\). A report should carry:
- the supported loss family and parameters;
- support cap \(b\) and margin \(\varepsilon_L\);
- the input moments or moment intervals and their feasible intersection;
- the numeric bound, proof method/status, and the two-point witness when applicable;
- an explicit indication that the uncertain-moment global maximum is or is not certified.

This is another instance of Great Scale's projection discipline: a single number is not enough unless its admissible set, witness, and proof status travel with it.

## Test / verify / run

test_loss_envelope.py covers the positive-third-derivative contract, witness reconstruction of mean/variance, reproducibility of the Descent LV log example, sampled Hermite-majorant checks, conservative chord bounds on discrete laws, zero-width support, and explicit rejection of invalid inputs.

Run:
~~~bash
npm test
python3 test_descent.py
python3 test_loss_envelope.py
npm run all
~~~

These are test commands, not asserted outcomes. The branch CI must actually execute them before the implementation can be called verified. Sampled pointwise checks support debugging; the analytic Hermite-remainder argument is the proof.


## Follow-on: Descent LVII boundary asymptotic

The fixed-moment log-loss envelope has an explicit singular-limit expansion as the support margin approaches zero. Descent LVII derives the limiting boundary mass, finite interior contribution, and first correction, and extends the regression suite with an epsilon sweep. See [DESCENT_LVII_BOUNDARY_ASYMPTOTIC_CLOSURE.md](DESCENT_LVII_BOUNDARY_ASYMPTOTIC_CLOSURE.md). This adds an asymptotic result without changing the LV/LVI proof-status boundary: fixed moments are sharp; the uncertain-moment global maximum is still not certified by a corner assumption.
