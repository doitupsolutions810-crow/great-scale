# Descent CXLVII — Quotient well-definedness is not continuity

## Finding

The canonical-coordinate contraction in `test_descent.py` is invariant under equivalent representatives, but it is not continuous at the quotient seam for the nontrivial contraction parameter (k=0.5).

Let (q:mathbb{R}\to\mathbb{R}/9\mathbb{Z}) be the quotient map and define, using the canonical representative (m(x)=x\bmod 9\in[0,9)),

\[
C_k(x)=4.5+k(m(x)-4.5).
\]

Fiber constancy holds:

\[
x-y\in9\mathbb Z\Rightarrow C_k(x)=C_k(y).
\]

That makes the formula well-defined as a set map on quotient classes. It does not establish continuity in the quotient topology.

At the seam:

\[
C_{0.5}(0)=2.25,\qquad
\lim_{x\to9^-}C_{0.5}(x)=6.75.
\]

Their circular distance is

\[
d_9(2.25,6.75)=\min(4.5,9-4.5)=4.5,
\]

so the one-sided jump is macroscopic, not numerical noise. The exact-representative test (C(0)=C(9)) passes while missing this discontinuity.

More generally, for (0<|k|<1), the seam's lifted outputs differ by (9|k|); the circular gap is nonzero except where the parameter difference is an integer multiple of the circumference. In the contraction range (|k|<1), only (k=0) removes this seam jump.

## Scientific interpretation

This is a distinction between three claims:

1. **Representative invariance:** equivalent inputs produce the same output.
2. **Continuity:** nearby quotient states produce nearby quotient outputs.
3. **Convergence:** iterates approach a fixed point.

None of these statements should be used as a synonym for another. The formula can be fiber-constant and its interior iterates can converge toward 4.5, while the induced map remains discontinuous at the identified endpoint.

## Great Scale mapping

Keep the channels explicit:

- State-space identity: (x\sim y\iff x-y\in9\mathbb Z).
- Well-definedness: (q(x)=q(y)\Rightarrow C_k(x)=C_k(y)).
- Continuity obligation: (d_9(C_k(9-\epsilon),C_k(0))\to0) as \(\epsilon\downarrow0).
- Convergence obligation: independently test (d_9(C_k^n(x),p)\to0), including starts straddling the seam.

The seam continuity obligation fails for (k=0.5), with limiting distance (4.5). The new executable test deliberately characterizes this defect so it cannot be mistaken for a passing continuity proof.

## Remediation choices

Do not merely add more exact endpoint-equality tests. Choose and document one of:

- If the state space is intended to be the quotient circle, replace the canonical-coordinate affine formula with a genuinely continuous circle map and test seam limits plus iteration behavior.
- If the affine contraction is intentional, change the state space/coordinate chart contract and stop describing it as a continuous circle contraction.

Any replacement must separately prove representative invariance, seam continuity, fixed-point behavior, and convergence. A continuity test does not by itself prove convergence or scientific validity.

## Verification boundary

The isolated CXLVII characterization test checks the formula and its one-sided limit numerically. It does not execute the full Great Scale suite or validate a physical model. Hosted CI and the full aggregate suite must run against the exact reviewed commit before repository-level verification is claimed.
