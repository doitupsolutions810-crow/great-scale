# Great Scale CXXXVII — Independent Solver Verification

## Audit result that motivated this rung
A fresh exhaustive enumeration of the CXXXVI example finds three feasible assignments,
not two: (A,A,B), (A,B,B), and (B,A,B). The (A,A,B) assignment satisfies the stated
count limits and has two A units and one B unit. Therefore the correct robust envelope
is [0.304, 0.322], not [0.308, 0.322]. The CXXXVI tests, documentation, and artifact
are corrected on this branch.

## Independent oracle
This rung adds an exhaustive oracle implemented separately from the CXXXVI solver.
It compares endpoint values and feasible assignment counts. It also checks a monotonicity
property: relaxing assignment constraints expands or preserves the feasible set, so the
minimum cannot rise and the maximum cannot fall.

## Equations
For feasible assignments \(\mathcal F\), the identified envelope is
\[
L^*=\min_{x\in\mathcal F}\frac{S+\sum_hm_h(x)L_h}{G},\qquad
U^*=\max_{x\in\mathcal F}\frac{S+\sum_hm_h(x)U_h}{G}.
\]
If \(\mathcal F_1\subseteq\mathcal F_2\), then
\[
L^*(\mathcal F_2)\le L^*(\mathcal F_1),\qquad
U^*(\mathcal F_2)\ge U^*(\mathcal F_1).
\]
This follows from minimum and maximum over nested feasible sets.

## Profound finding
Verification is not only checking that code runs; it is checking that the feasible set
matches the stated model. The earlier count error demonstrates that a correct optimization
formula can still produce a wrong reported result when a feasible assignment is overlooked.
An independent oracle and assignment-count assertions make this failure mode observable.

## Scope
The oracle is practical only for small assignment spaces. Test files are authored but have
not been run in repository CI during this turn. No empirical validity or population coverage
is claimed.
