# Descent LXXXI — quotient-consistent heat in the descent engine

**Status:** source-level defect found; proposed fix and regression tests committed on a research branch. The repository test suite has not yet been executed in this environment.

## Profound finding

Great Scale defines its discrete reflection on the ninefold circle \(\mathbb R/9\mathbb Z\):
\[
f(x)=\bigl(9-(x\bmod 9)\bigr)\bmod 9.
\]
Therefore \(x\) and \(x+9k\) represent the same circle point. But the descent engine previously computed
\[
S_{raw}(x)=\operatorname{heat}(x/9)=(x/9)(1-x/9)
\]
without canonicalizing the representative. This is not a function on the quotient: for example,
\[
S_{raw}(1)=\frac{8}{81}>0,\qquad
S_{raw}(10)=\frac{10}{9}\left(-\frac19\right)=-\frac{10}{81}<0,
\]
although \(1\equiv10\pmod9\). The second value violates the advertised heat range \([0,1/4]\), and if used as \(\Psi=\mathrm{CONE}+S\), it can falsely appear to breach the cone floor. The involution canonicalized coordinates, while the descent engine did not: the two modules disagreed about what a state is.

This is not a failure of the heat inequality. It is a representation-invariance failure at the interface between quotient geometry and the scalar observable.

## Correct contract

Canonicalize before applying interval descent:
\[
c(x)=((x\bmod9)+9)\bmod9\in[0,9),
\]
\[
x_{t+1}=4.5+k(c(x_t)-4.5),\qquad
S_t=\operatorname{heat}(c(x_{t+1})/9).
\]
For \(|k|<1\), the contraction theorem applies to the canonical interval representative. Equivalent inputs must produce equivalent first-step records:
\[
x\equiv y\pmod9\;\Longrightarrow\;
(x_1,S_1,f(x_1))=(y_1,S_1,f(y_1))
\]
for the engine's canonicalized update.

Since \(0\le c(x)/9<1\), the heat bound follows:
\[
0\le S_t\le\frac14,\qquad
\phi^{-2}\le\Psi_t=\phi^{-2}+S_t\le\phi^{-2}+\frac14.
\]
Numerically, \(0.381966\lesssim\Psi_t\lesssim0.631966\).

## Great Scale mapping — Levels 9701–9710

- **9701 — Quotient identity:** state observables must be invariant under \(x\mapsto x+9k\).
- **9702 — Canonical representative:** normalize to \([0,9)\) before applying interval formulas.
- **9703 — Bounded heat:** reject or normalize any path that can produce \(S<0\) or \(S>1/4\).
- **9704 — Dynamics contract:** state the domain where the contraction theorem applies; \(|k|<1\) alone does not repair inconsistent coordinates.
- **9705 — Mirror parity:** browser ESM and Node CJS implementations must implement the same transition.
- **9706 — Regression witness:** compare starts \(1\) and \(10\), plus negative and multi-turn representatives.
- **9707 — Cone safety:** only derive \(\Psi\ge\mathrm{CONE}\) after validating the heat domain.
- **9708 — Boundary semantics:** \(0\equiv9\) must be handled by canonicalization, not by relying on a single endpoint test.
- **9709 — Evidence discipline:** source inspection and a regression test are not the same as a passing test run.
- **9710 — Promotion gate:** require the repository's complete test commands and exact-head CI before merging.

## Verification ledger

- **Source inspection:** confirmed the mismatch in both `public/scale.js` and `public/scale.cjs`.
- **Change proposed:** both mirrors now canonicalize the engine input before contraction and normalize the heat coordinate; tests compare equivalent representatives and check bounded heat for negative/multi-turn starts.
- **Not yet run:** `npm test`, `python3 test_descent.py`, `npm run all`, browser UI, and hosted CI. A container attempt to clone GitHub failed because this environment could not resolve `github.com`; do not treat the new tests as passed.
- **Scope:** a software/model consistency result, not a new physical law or empirical claim.

## Candidate principle

**A quotient-defined state cannot have representative-dependent observables.** If a Great Scale observable changes when a coordinate is replaced by an equivalent representative, it is not yet a well-defined observable on the declared geometry.
