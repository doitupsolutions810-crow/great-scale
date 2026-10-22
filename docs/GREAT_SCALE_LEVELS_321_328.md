# Great Scale Descent LXXXIX — Evidence-chain closure (Levels 321–328)

**Status labels:** the interval theorem below is a derived result under the stated scalar model; the promotion rule is a proposed engineering invariant; the cross-repository observations are source-level findings; physical interpretation is unresolved.

## 321 — The scalar certificate

Assume
\[
0\le p\le1,\qquad v\ge0,\qquad g(p,v)=p(1-p)-v.
\]
For bounded uncertainty, clip the admissible box to
\[
p\in[p_-,p_+]\subseteq[0,1],\qquad v\in[v_-,v_+],\quad v_-\ge0.
\]
Because (p(1-p)) is concave,
\[
g_{\min}=\min\{p_-(1-p_-),p_+(1-p_+)\}-v_+,
\]
and
\[
g_{\max}=\max_{p\in[p_-,p_+]}p(1-p)-v_-.
\]
Thus (g_{\min}\ge0) certifies every admissible point feasible; (g_{\max}<0) certifies every admissible point infeasible; otherwise the box is unresolved. Exact rational arithmetic certifies this model and input representation, not a physical probability distribution without empirical assumptions.

## 322 — The integration contract

The combined candidate includes the helper, six regression tests, its documentation, and one canonical verification script. The script's required order is:
1. JavaScript regression suite.
2. Robust-feasibility regression suite.
3. Python descent suite.

Each outcome is recorded separately as `passed`, `failed`, or `not_run`. A suite that never starts is not a passing suite and must not be represented as a failed assertion.

## 323 — The branch-coverage contract

The candidate workflow is configured for pushes to the integration branch and pull requests targeting the hardened research branch. This closes the known target-branch filter gap in workflow configuration. It does not establish that GitHub provisioned a runner or that the workflow executed.

## 324 — Evidence is not self-authenticating

A locally generated receipt can summarize what its process observed. It cannot, by its own contents, prove that it came from a trusted runner. Stronger evidence requires platform-observed run identity, the exact candidate SHA, executed steps and logs, and an artifact bound to that same run. A missing runner or missing logs leaves the result unverified.

## 325 — The composition rule

Let the candidate SHA be (s), and define:
- (F(s)): formal/model assumptions are declared;
- (I(s)): implementation corresponds to the declared model;
- (T(s)): every required suite actually ran and passed;
- (E(s)): execution evidence is bound to (s) and is independently retrievable;
- (A(s)): the authorized promotion decision is current and refers to (s).

The proposed promotion invariant is
\[
\operatorname{Promote}(s)\Rightarrow
F(s)\land I(s)\land T(s)\land E(s)\land A(s).
\]
This is a governance contract, not a theorem that the repository currently enforces end-to-end. Its key feature is the shared index (s): evidence about one commit cannot silently certify another.

## 326 — Failure classification

Keep distinct:
- **pass:** required assertions executed and passed;
- **test failure:** the runner executed a suite and an assertion/process failed;
- **infrastructure-blocked:** no runner/steps or usable execution evidence;
- **not_run:** a required suite was not reached;
- **unresolved:** available evidence does not decide the claim.

Conflating infrastructure-blocked with test failure destroys diagnostic information; conflating it with pass destroys assurance.

## 327 — Verification record for this descent

- The six robust-feasibility cases passed in an isolated local reproduction of the helper logic.
- The exact GitHub candidate branch was source-inspected for the helper, test module, canonical script, and workflow configuration.
- The full repository suites, complete build, and exact-head hosted run are **not verified** here. No merge or deployment is claimed.
- The candidate preserves (Psi=\mathrm{CONE}+S), (S=h(1-h)), (mathrm{CONE}=\phi^{-2}). It does not identify that convention with the separate provisional relation (Psi=H-\sigma).

## 328 — Profound finding: correctness must survive transport

A mathematical statement can be correct while the implementation is wrong; an implementation can be correct while the intended tests never run; tests can pass on a different commit; and a receipt can be structurally valid without being authentic. Therefore, the object that deserves promotion is not merely a formula, code revision, green-looking status, or receipt. It is the **commit-bound chain of justified transitions** from assumptions to derivation, implementation, execution, evidence, and authorized action.

This is an engineering/epistemic conclusion. It is not evidence for a new physical law or for quantum-geometry claims.
