# Great Scale CXLI — Minimal Sufficient State

## Question

When is a compressed state a lossless representation of the assignments that
it merges?

## Finite-model criterion

Let \(\mathcal A\) be a finite set of assignments, \(K(a)\) a proposed
compressed-state key, and \(O(a)\) the complete downstream outcome signature.
The signature should include every distinction relevant to the task, such as
feasibility, objective values, resource use, or constraint residuals.

The key is sufficient on this finite domain exactly when

\[
K(a)=K(b)\;\Longrightarrow\;O(a)=O(b)
\qquad\text{for all }a,b\in\mathcal A.
\]

Equivalently, each fiber \(K^{-1}(k)\) must be outcome-homogeneous. A
counterexample pair with equal keys and unequal signatures disproves
sufficiency for the tested domain. Passing exhaustive enumeration establishes
only finite-domain sufficiency for the chosen signature; it does not prove
that the signature includes every relevant future consequence.

## Worked counterexample

For two units, use unit-specific contributions:

- Unit 1: A = (0.0, 0.1), B = (0.4, 0.5)
- Unit 2: A = (0.2, 0.3), B = (0.8, 0.9)

Assignments AB and BA both have category counts (A=1, B=1), but:

\[
O(AB)=(0.8,1.0),\qquad O(BA)=(0.6,0.8).
\]

So counts alone are not sufficient. A refined key containing category counts
and accumulated lower/upper sums separates these assignments. This is an
example of a sufficient key for these observed additive outcomes, not a
claim that this key is minimal for every model.

## Algorithm

1. Enumerate the finite assignment set.
2. Group assignments by the proposed state key.
3. Compare outcome signatures inside each group.
4. Return collision witnesses whenever a group contains unequal signatures.
5. Test a refined key against the same oracle.

Time is linear in the number of assignments plus signature comparisons for
this simple implementation; the number of assignments itself can grow
exponentially with the number of units.

## Great Scale mapping

- **Invariant sought:** outcome signature is constant on every compressed-state fiber.
- **Failure signal:** same key, different outcome — state aliasing.
- **Repair:** retain a statistic that distinguishes the counterexample, then
  rerun the audit.
- **Scientific boundary:** the audit verifies the encoded finite model and
  declared signature, not empirical truth or an unspecified future process.

## Test status

Four unit tests are provided: homogeneous count-state sufficiency,
heterogeneous count-state failure with explicit collision values, refinement,
and feasibility sensitivity. They are authored but were not executed by this
integration action.
