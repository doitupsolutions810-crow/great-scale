# Descent XCV — Quotient well-definedness is not continuity

## Finding

The current \`test_descent.py\` defines

\[
C_k(x)=4.5+k\left((x\bmod 9)-4.5\right),\qquad 0\le (x\bmod9)<9.
\]

Canonicalization makes this function **fiber-constant**: if \(x-y\in9\mathbb Z\), then \(C_k(x)=C_k(y)\). Therefore it defines a set map on equivalence classes in \(\mathbb R/9\mathbb Z\).

That fact does **not** imply that the descended map is continuous in the quotient topology. The chosen canonical representative jumps from \(9^-\) to \(0^+\) at the seam. The one-sided output limits are

\[
\lim_{x\to9^-}C_k(x)=4.5+4.5k,\qquad
\lim_{x\to0^+}C_k(x)=4.5-4.5k.
\]

When outputs are interpreted on the same circle, the seam gap is

\[
d_9=\min(9|k|,\;9-9|k|)\quad\text{for }0\le|k|\le1.
\]

For the default \(k=0.5\), the limits are \(6.75\) and \(2.25\), and their circular distance is \(4.5\), not zero. The map is therefore discontinuous at the quotient seam. For the usual contraction range \(0<|k|<1\), the seam gap is nonzero; within \(0\le k\le1\), the seam is continuous only at the endpoint cases \(k=0\) (constant) and \(k=1\) (identity).

## Why this matters

- **Algebraic invariant:** \(C_k(x+9n)=C_k(x)\) is satisfied.
- **Topological invariant:** continuity on \(\mathbb R/9\mathbb Z\) is not satisfied for the default \(k=0.5\).
- **Dynamical observation:** iterating the canonicalized formula converges toward \(4.5\) for the tested representatives, but convergence of iterates does not repair discontinuity of the one-step map.
- **Interpretation boundary:** describe the current function as a representative-dependent, fiber-constant contraction rule, not as a continuous contraction of the circle.

A related topological constraint is that the circle is not contractible: its identity map is not homotopic to a constant map. This does not prohibit continuous self-maps or iterative dynamics; it cautions against treating a global continuous contraction-to-a-point as an ordinary circle contraction without changing the state space or assumptions.

## Independent numerical check

For \(k=0.5\):

| Quantity | Value |
|---|---:|
| \(C_k(0)\) | 2.25 |
| \(\lim_{x\to9^-}C_k(x)\) | 6.75 |
| Circular seam distance | 4.5 |
| \(C_k(0)=C_k(9)\) after canonicalization | true |
| Continuity at the seam on the quotient circle | false |

The equality \(C_k(0)=C_k(9)\) compares two exact representatives after canonicalization; it does not compare the left-hand limit as \(x\to9^-\). This is the precise distinction the existing seam test does not capture.

## Great Scale mapping

| Channel | Current meaning | Required interpretation |
|---|---|---|
| Modulo/fiber constancy | Representation invariance | Keep the existing \(C_k(x+9n)=C_k(x)\) check |
| Circular distance \(d_9\) | Geometry of the quotient state space | Add a one-sided seam-continuity diagnostic |
| Iterative convergence to \(4.5\) | Dynamics under repeated canonicalized updates | Do not infer continuity from convergence |
| Involution \(x\mapsto9-x\pmod9\) | Separate symmetry channel | Keep it distinct from the contraction rule |
| Canonical phase-driven state | Existing Great Scale state channel | Do not silently redefine it while changing the quotient map |

## Recommended test additions

1. Keep the existing fiber-constancy tests at \(0\) and \(9\), \(4.5\) and \(13.5\), and negative representatives.
2. Add a left-seam sequence \(x_n=9-\epsilon_n\) and verify its outputs approach \(6.75\) for \(k=0.5\).
3. Compare that limit with \(C_k(0)=2.25\) using the circular metric and assert the gap approaches \(4.5\).
4. Name the behavior explicitly as a discontinuity, unless the design is changed to use a genuinely continuous circle map. Do not write a test that incorrectly equates fiber constancy with continuity.

## Verification status

The boundary limits and seam distance are direct algebraic consequences of the implemented formula. A separate numerical check should verify the limits. The full Great Scale suite (\`npm test\`, \`python3 test_descent.py\`, and \`npm run all\`) remains unverified unless separately executed against an exact checkout. This is a mathematical/code-semantics finding, not a physical claim.
