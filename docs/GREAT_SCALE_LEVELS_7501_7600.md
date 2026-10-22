# Great Scale — Levels 7501–7600: public transition-domain coherence

## Profound finding

The engine and the exported single-step API did not implement the same state space. \`DescentEngine\` canonicalized each coordinate to the ninefold circle before applying contraction, but \`descentStep(x,k)\` forwarded an arbitrary finite real coordinate directly to \`softContract\`. Equivalent circle representatives could therefore yield different public transitions, and the heat invariant attached to the circle state could fail outside its intended domain.

For \(k=\tfrac12\), the real-line formula is

\[
C(x)=4.5+\tfrac12(x-4.5).
\]

At \(x=1\), \(C(1)=2.75\). But the equivalent circle representative \(x=19\equiv1\pmod9\) produced \(C(19)=11.75\) through the old public API. If this output is interpreted as a normalized circle height, then \(h=11.75/9=47/36>1\) and

\[
S(h)=h(1-h)=\frac{47}{36}\left(-\frac{11}{36}\right)=-\frac{517}{1296}<0,
\]

contradicting the advertised \(0\le S\le\tfrac14\) heat bound. The engine path avoided this particular failure; the public one-step path did not.

## Contract repair

Define the public circle transition as

\[
D_k(x)=4.5+k\left(\operatorname{mod}_9(x)-4.5\right),\qquad
\operatorname{mod}_9(x)=((x\bmod9)+9)\bmod9.
\]

For finite \(x\) and \(|k|<1\), \(\operatorname{mod}_9(x)\in[0,9)\). For any \(x_c\in[0,9)\) and \(-1<k<1\), \(D_k(x_c)=4.5+k(x_c-4.5)\) lies in \((0,9)\), because \(|x_c-4.5|\le4.5\) and \(|k(x_c-4.5)|<4.5\). Therefore \(h=D_k(x)/9\in[0,1]\) and \(S=h(1-h)\in[0,1/4]\).

The ES module and CommonJS \`descentStep\` now canonicalize before contraction. The Python reference test module now exposes the corresponding \`descent_step\` function. \`softContract\` remains the real-line affine primitive; canonicalization belongs to the circle-domain API.

## Great Scale mapping

**Level 7501 — State-space identity.** Circle representatives \(x\) and \(x+9n\), for integer \(n\), represent the same state.

**Level 7502 — Transition invariance.** The public circle transition satisfies \(D_k(x+9n)=D_k(x)\), because both inputs map to the same canonical representative.

**Level 7503 — Invariant preservation.** With \(h=D_k(x)/9\in[0,1]\), the quadratic \(S(h)=h(1-h)\) obeys

\[
S(h)=\tfrac14-(h-\tfrac12)^2\in[0,\tfrac14].
\]

**Level 7504 — Cross-runtime contract parity.** ES module, CommonJS, and Python reference logic should agree on normalization and the resulting transition.

**Level 7505 — Separate primitive from domain API.** \`softContract\` remains a real-line map; \`descentStep\` is the circle-state operation. Explicit boundaries prevent callers from assuming the wrong geometry.

## Verification boundary

Regression cases cover negative coordinates, canonical representatives, seam-equivalent values, the former counterexample \(1\) versus \(19\), and the heat bound. Source changes and targeted checks do not, by themselves, establish that the repository's complete \`npm run all\` suite or hosted deployment passed. Report those separately after execution against the exact commit.
