# Great Scale research note: bounded feasibility certification

**Status:** research helper / candidate integration; not a change to the live state model.

## Preserved project convention

The current Great Scale README and source module define the existing observable as

\[
\Psi = \mathrm{CONE} + S, \qquad S=h(1-h), \qquad \mathrm{CONE}=\phi^{-2}.
\]

This note does **not** replace that convention with the separate provisional research relation \(\Psi=H-\sigma\). Any future mapping between these representations requires an explicit, versioned definition and proof of its assumptions.

## Constraint being certified

For the separate probability-moment model, assume

\[
0\leq p\leq1,\qquad v\geq0,\qquad g(p,v)=p(1-p)-v\geq0.
\]

Given nominal values \((p,v)\) and bounded errors \(\epsilon_p,\epsilon_v\), consider the uncertainty box intersected with the declared domain. Because \(p(1-p)\) is concave, its minimum over a closed interval occurs at an endpoint and its maximum occurs at \(p=1/2\) if that point is in the interval, otherwise at an endpoint.

Let \([p_-,p_+]\) and \([v_-,v_+]\) be the clipped intervals. Then

\[
g_{\min}=\min\{p_-(1-p_-),p_+(1-p_+)\}-v_+,
\]

\[
g_{\max}=\max_{p\in[p_-,p_+]}p(1-p)-v_-.
\]

Classification:

- **certified_feasible** if \(g_{\min}\geq0\): every admissible point in the box satisfies the constraint.
- **certified_infeasible** if \(g_{\max}<0\): no admissible point in the box satisfies the constraint.
- **unresolved** otherwise.

The implementation uses exact rational arithmetic based on each input's decimal string representation. The result is an exact certificate for this scalar box model, not a statistical confidence interval, general nonlinear proof engine, or empirical physics result.

## Run

\`\`\`bash
python3 -m unittest -v test_robust_feasibility.py
npm test
python3 test_descent.py
\`\`\`

The canonical verification script runs all three suites and records each suite's status separately in the receipt.
