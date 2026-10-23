# Great Scale Descent XC — Execution evidence and identity (Levels 321–336)

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
Because $p(1-p)$ is concave,
\[
g_{\min}=\min\{p_-(1-p_-),p_+(1-p_+)\}-v_+,
\]
and
\[
g_{\max}=\max_{p\in[p_-,p_+]}p(1-p)-v_-.
\]
Thus $g_{\min}\ge0$ certifies every admissible point feasible; $g_{\max}<0$ certifies every admissible point infeasible; otherwise the box is unresolved. Exact rational arithmetic certifies this model and input representation, not a physical probability distribution without empirical assumptions.

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

Let the candidate SHA be $s$, and define:
- $F(s)$: formal/model assumptions are declared;
- $I(s)$: implementation corresponds to the declared model;
- $T(s)$: every required suite actually ran and passed;
- $E(s)$: execution evidence is bound to $s$ and is independently retrievable;
- $A(s)$: the authorized promotion decision is current and refers to $s$.

The proposed promotion invariant is
\[
\operatorname{Promote}(s)\Rightarrow F(s)\land I(s)\land T(s)\land E(s)\land A(s).
\]
This is a governance contract, not a theorem that the repository currently enforces end-to-end. Its key feature is the shared index $s$: evidence about one commit cannot silently certify another.

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
- The candidate preserves $\Psi=\mathrm{CONE}+S$, $S=h(1-h)$, $\mathrm{CONE}=\phi^{-2}$. It does not identify that convention with the separate provisional relation $\Psi=H-\sigma$.

## 328 — Finding: correctness must survive transport

A mathematical statement can be correct while the implementation is wrong; an implementation can be correct while the intended tests never run; tests can pass on a different commit; and a receipt can be structurally valid without being authentic. Therefore, the object that deserves promotion is not merely a formula, code revision, green-looking status, or receipt. It is the **commit-bound chain of justified transitions** from assumptions to derivation, implementation, execution, evidence, and authorized action.

This is an engineering/epistemic conclusion. It is not evidence for a new physical law or for quantum-geometry claims.

## 329 — The exact-head execution probe

For candidate SHA `d8fc61bee05b2efc55e1eef3c17a60d0f1c6008f`, GitHub returned workflow run `39826309026` with conclusion `failure`. The associated job has no retrievable log URL, no exposed steps, and no receipt artifact. This is consistent with the pre-existing runner-start blocker documented in issue #90. The available evidence does **not** show that a test assertion ran or failed.

Classification: **infrastructure-blocked / unverified**, not pass and not source-test failure.

## 330 — A deployment is not a test

The PR conversation also records a Vercel deployment rate-limit error (`api-deployments-free-per-day`). That is a deployment-service quota event. It neither validates nor falsifies the Python/JavaScript suites, and it is not evidence of a mathematical defect. Keep build/deploy status separate from test status.

## 331 — Receipt provenance gap

The receipt records the checked-out commit and GitHub run metadata, but the receipt itself is generated by the same process it describes. Its fields are useful for correlation, not a cryptographic attestation. The assurance chain still needs platform evidence that the run ID, run head SHA, job steps, logs, and downloaded artifact agree. If any link is absent, the outcome remains unresolved.

## 332 — Identity is an invariant, not a display label

Cross-repository source review identified two related risks:
- CycleKernal simulation randomness and wall-clock timestamps prevent deterministic replay unless RNG state/seed, initial configuration, code revision, and event ordering are explicit.
- TrainLLM's truncated `user_id[:6]` identity can collide, and a default `mock_human` signature string is not cryptographic authorization.

These are source-level findings, not evidence of an exploited attack. They share one structural defect: an identity or execution context is being represented by a value that does not uniquely bind the intended object and history.

## 333 — Replayability condition

A reproducible simulation should be treated as a function of an explicit execution record:
\[
R = f(C, X_0, \omega, O, V),
\]
where $C$ is the code revision, $X_0$ the initial state/configuration, $\omega$ the explicit RNG state or seed, $O$ the stable event order, and $V$ the runtime/dependency contract. This is a design specification; determinism still requires testing and control of nondeterministic dependencies.

## 334 — The chain-of-custody invariant

For a verification artifact $a$ and candidate commit $s$, define a binding predicate $B(a,s)$ that requires:
1. a platform-observed run for $s$;
2. actual required steps and retrievable logs;
3. an artifact emitted by that same run;
4. receipt commit and platform run-head SHA equal to $s$;
5. no missing required suite.

Then a useful promotion precondition is
\[
\operatorname{Eligible}(s)\Rightarrow B(a,s)\land T(s)\land A(s).
\]
This is a proposed assurance contract. It becomes an enforced invariant only when code and repository rules actually gate promotion on it.

## 335 — Current gate result

For PR #97, the hosted run is recorded as failed but has no steps/logs and produced no receipt artifact. The isolated six-test reproduction is useful preliminary evidence, but it is not a substitute for running the committed module and all repository suites on the exact head. PR #97 therefore remains a draft candidate; no merge or deployment is authorized by this evidence.

## 336 — Profound finding: preserve the chain, not merely the state

Across mathematical certification, simulation replay, user identity, authorization, and CI, the common requirement is **referential integrity across transformations**: the claim, the model, the execution, the evidence, and the authorized action must all refer to the same well-defined object and history. A system can preserve a numerical invariant while losing the provenance needed to know what that number means. In Great Scale terms, preserving a value is weaker than preserving the conditions under which that value is justified.

This is a cross-domain engineering insight, not a demonstrated physical law. Any physical interpretation remains unresolved until independently defined and empirically or mathematically supported.
