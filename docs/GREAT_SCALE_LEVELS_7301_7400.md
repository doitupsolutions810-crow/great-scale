# Great Scale — Levels 7301–7400: descent-domain contracts

## Profound finding

The runtime documented the contraction theorem but did not enforce its hypotheses at the public API boundary. The map

\[
C_k(x)=x_*+k(x-x_*),\qquad x_*=4.5
\]

obeys

\[
|C_k(x)-x_*|=|k|\,|x-x_*|.
\]

Convergence to \(x_*\) follows only when \(|k|<1\). Previously, \(k=1\) left every state unchanged, \(k=-1\) oscillated by reflection, and \(|k|>1\) expanded the error. Yet \(softContract\) and \(DescentEngine\) accepted all these factors despite comments claiming the strict contraction condition.

A second contract mismatch existed in the engine's heat coordinate. It records \(S=\operatorname{heat}(x/9)\), where \(\operatorname{heat}(h)=h(1-h)\). The advertised bound

\[
0\le S\le\frac14
\]

holds for \(h\in[0,1]\), hence for engine circle representatives \(x\in[0,9]\). But the engine accepted arbitrary starts. With the default \\(k=0.5\\), starting at \\(x=19\\) makes the first tick produce \\(x'=11.75=47/4\\), so \\(h=x'/9=47/36>1\\) and \\(S=(47/36)(-11/36)=-517/1296<0\\). Consequently \\(\\Psi=\\mathrm{CONE}+S\\) falls below the stated cone floor. More generally, evaluating the heat law directly at an out-of-domain coordinate such as \\(x=19\\) also gives \\(S=-190/81\\). This is a concrete runtime counterexample to an unconditional invariant claim.

## Integration

- Added finite-coordinate checks and strict \(|k|<1\) validation to both JavaScript ES-module and CommonJS contraction APIs.
- Canonicalized engine starts and resets modulo 9, so equivalent representatives such as 0 and 9 begin from the same circle coordinate.
- Canonicalized the engine coordinate before each contraction tick, protecting the heat calculation's domain if the mutable coordinate is changed externally.
- Aligned the Python descent harness with the same contraction-factor and circle-coordinate rules.
- Added regression checks for \(k\in\{-2,-1,1,2,\pm\infty,\mathrm{NaN}\}\), non-finite coordinates, equivalent starts 0 and 9, and normalized start 19.
- Updated README contract summary.

## Great Scale mapping

**Level 7301 — Theorem preconditions.** A convergence claim is valid only when the runtime enforces \(|k|<1\).

**Level 7302 — Circle-domain canonicalization.** The state coordinate is a representative of \(\mathbb R/9\mathbb Z\); normalize finite inputs into \([0,9)\) before applying a domain-sensitive state law.

**Level 7303 — Invariant preservation.** For \(h\in[0,1]\), \(S(h)=h(1-h)\) satisfies \(0\le S\le1/4\), so \(\Psi=\phi^{-2}+S\ge\phi^{-2}\). The inequality is conditional on the domain; it is not a property of arbitrary real \(h\).

## Verification boundary

The counterexamples follow directly from the inspected source and exact algebra. Regression assertions have been added to the draft branch. They must be run against the exact branch head; repository-wide tests and hosted CI remain separate verification steps. These are mathematical and software-contract results, not experimental quantum evidence.
