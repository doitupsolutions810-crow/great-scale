# Great Scale CXLIII — Optimization-Preserving Compression

## Question

Does a compressed state preserve the actual optimization problem, rather than merely looking like a good summary?

For finite assignments \(\mathcal A\), let \(K(a)\) be a proposed state key, \(F(a)\in\{0,1\}\) feasibility, and \(J(a)\) the objective. A conservative state-level criterion is:
\[
K(a)=K(b)\Rightarrow F(a)=F(b),
\]
and, whenever feasible,
\[
K(a)=K(b)\Rightarrow J(a)=J(b).
\]
These conditions preserve feasibility and objective meaning within each compressed state. They imply that taking one representative per state preserves the minimum objective, provided the compressed problem uses the same feasible state classes.

Equality of optimum alone is weaker: a broken compression may coincidentally return the same minimum while misrepresenting feasibility or other feasible assignments.

## Tests

Four tests cover: a safe outcome-equivalence key; a feasible/infeasible collision; different objective values merged into one state; and an over-refined key that retains correctness but provides less compression.

## Scientific boundary

This is an exhaustive finite-domain audit. It does not prove that the assignment domain is complete, that the feasibility predicate encodes every real constraint, or that a state remains sufficient under future transitions not represented in the audit.

The reference implementation is quadratic in assignments for pairwise homogeneity checks and is intended as a small-instance verifier.

## Great Scale mapping

- **Invariant:** equal compressed keys preserve feasibility and objective.
- **Counterexample:** a key group mixes feasible and infeasible assignments or different feasible objective values.
- **Optimization check:** compare original and compressed minima.
- **Important distinction:** matching minima alone does not establish full problem equivalence.
