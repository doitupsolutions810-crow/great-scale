# Great Scale LXXXVIII — Sequential Evidence, Multiple Testing, and the Stopping Boundary

## Descent question

LXXXVII allowed a hidden-common-cause candidate to become eligible for review after independent validation. The next risk is repeated searching: if a system tests many candidate dependencies, repeatedly checks the same stream, and stops only when a favorable score appears, a fixed single-look threshold no longer automatically has its advertised error rate.

## Mathematics

### 1. Allocate a family-wise error budget

For a predeclared family of \(m\) candidate tests and total error budget \(\alpha\), Bonferroni allocation gives

\[
\alpha_i=\frac{\alpha}{m},\qquad
\sum_{i=1}^{m}\alpha_i=\alpha.
\]

By the union bound, if each test's false-positive probability is controlled at its allocated level, the probability of one or more false positives in the family is at most \(\alpha\). This is conservative and requires the individual tests' guarantees to be valid. Candidate discovery that continues indefinitely needs a suitable online allocation policy; the fixed-family formula alone does not solve that problem.

### 2. Correct for repeated looks with an anytime-valid process

For a valid nonnegative e-process \((E_t)\) under null hypothesis \(H_0\), Ville's inequality states

\[
P_{H_0}\!\left(\sup_{t\ge0}E_t\ge\frac1\alpha\right)\le\alpha.
\]

Thus the boundary \(1/\alpha\) can control false crossings over repeated looks, provided the process really is valid under the null. An arbitrary confidence score, posterior odds, or likelihood score is not automatically an e-process. At \(\alpha=0.05\), the threshold is 20. If ten candidate tests share a family-wise budget of 0.05 using Bonferroni, each gets 0.005 and its corresponding anytime-valid threshold is 200.

Not crossing the boundary is **not** proof of the null: the result remains continue/inconclusive unless a separate, valid rejection/acceptance design says otherwise.

### 3. Fixed-hypothesis sequential likelihood ratio

For a classical sequential probability ratio test with simple hypotheses and suitable sampling assumptions, the familiar Wald boundaries are

\[
A\approx\frac{1-\beta}{\alpha},\qquad
B\approx\frac{\beta}{1-\alpha}.
\]

A likelihood ratio at or above \(A\) favors \(H_1\); at or below \(B\) favors \(H_0\); between them, continue sampling. These are Wald approximations, not universal exact finite-sample guarantees. The sampling model, hypotheses, dependence structure, and stopping protocol must be specified.

## Worked example

Suppose a system proposes ten hidden dependency edges and the family-wise false-positive budget is 5%.

\[
\alpha_i=0.05/10=0.005,\qquad 1/\alpha_i=200.
\]

A candidate e-process reaching 200 crosses its allocated statistical boundary. That makes the candidate eligible for review—not automatically causal, not automatically merged into the dependency graph, and not automatically safe to use in production. The process must be valid, the candidate must survive independent validation, and causal claims need appropriate design (for example, a controlled intervention where feasible).

## Integration with LXXXV–LXXXVII

- **LXXXV:** enumerate declared dependency failures and minimal cut sets.
- **LXXXVI:** bound reliability conditional on the declared model and stated incompleteness assumptions.
- **LXXXVII:** propose hidden causes, then validate on data independent of discovery.
- **LXXXVIII:** constrain the search itself with a declared error budget and stopping rule. Recompute downstream cut sets and residual-risk bounds only after a reviewed model change; preserve the previous graph and provenance.

## Pinned finding

**The stopping rule is part of the evidence.** A system that can search until a favorable result appears cannot simply reuse a single-look threshold and claim its original error rate. Reliable adaptation requires a declared error budget, a valid sequential procedure, and an explicit inconclusive state.

## Scientific limits and validation plan

This is a mathematical/statistical control design, not empirical proof that any live system is calibrated. Before operational use: (1) preregister or version the candidate family and error allocation; (2) verify e-process assumptions against the actual data-generation and dependence structure; (3) test null simulations and alternative scenarios; (4) retain all looks, rejected candidates, and stopping decisions; (5) use independent validation and intervention where causal attribution is required. If these assumptions cannot be justified, report the result as uncalibrated/inconclusive rather than claiming controlled error.
