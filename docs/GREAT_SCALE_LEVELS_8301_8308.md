# Great Scale — Levels 8301–8308: Trajectory Identity and Semigroup Consistency

## Finding

Matching the first transition and proving convergence are necessary but not sufficient for runtime equivalence. The stronger contract is equality of the full transition trajectory under the same initial state and parameter contract.

Let the Great Scale contraction be

\[
T_k(x)=x^*+k(x-x^*),\qquad x^*=4.5.
\]

Repeated application gives

\[
T_k^n(x)=x^*+k^n(x-x^*).
\]

For a fixed k, the maps form a semigroup:

\[
T_k^m(T_k^n(x))=T_k^{m+n}(x).
\]

But two valid contractions with |k1|<1 and |k2|<1 can both converge to the same fixed point while producing different intermediate states. Therefore a convergence-only acceptance test can certify the wrong dynamics.

## Great Scale map

| Level | Mathematics | Science / engineering meaning | Test gate |
|---|---|---|---|
| 8301 | T_k(x)=x*+k(x-x*) | Define the one-step transition contract | Check canonical default |
| 8302 | e_n=k^n e_0 | Derive the complete trajectory | Compare iterative and closed-form values |
| 8303 | T_k^m composed with T_k^n equals T_k^(m+n) | Repeated execution must compose consistently | Check 4+7 steps against 11 steps |
| 8304 | k1 differs from k2 implies trajectories differ in general | Same attractor does not imply same model | Contrast canonical k=phi^-2 with k=0.5 |
| 8305 | Default trajectory equals explicit canonical trajectory | Defaults are part of the model contract | Compare all states, not just the first |
| 8306 | A test result is a predicate over a trajectory and a revision | Acceptance criteria must target intended behavior | Regression checks cover multiple initial states and steps |
| 8307 | Convergence and behavioral equivalence are distinct properties | Avoid false confidence from weak tests | Require both stability and parity gates |
| 8308 | Runtime parity requires same initial domain, transition law, parameters, and step semantics | Contract equality is stronger than shared asymptotics | Exact-head cross-runtime suite remains required |

## Verification

The committed Python regression harness adds checks for:
- closed-form agreement over 13 points of each 12-step trajectory for four initial states;
- semigroup composition (4 steps followed by 7 versus 11 direct steps);
- equality of default and explicit canonical-parameter trajectories;
- the counterexample that k=0.5 can converge to the same fixed point while not matching the canonical trajectory.

These are deterministic numerical regression tests of the software model. They do not establish a physical or quantum-geometry result.

## Limits and promotion gate

The new checks are authored in test_descent.py. They must be executed from the actual repository checkout, together with npm test and the canonical verification script, on the exact reviewed commit. Hosted CI has historically failed before exposing runner steps or logs; until a normal run and same-run receipt are available, repository-wide verification and build status remain unverified.
