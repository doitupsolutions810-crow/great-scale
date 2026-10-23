# Great Scale Descent XI — Quantifiers, boundaries, and justified claims (Levels 337–344)

**Status labels:** Levels 337–340 are derived mathematics under the stated scalar model; Level 341 is a test-design change whose execution is pending; Levels 342–344 are engineering interpretations, not new physical laws.

## 337 — A certificate is a quantified statement

Let the admissible uncertainty set be a nonempty compact box
\[
B=[p_-,p_+]\times[v_-,v_+],\quad 0\le p_-\le p_+\le1,\quad 0\le v_-\le v_+,
\]
and let
\[
g(p,v)=p(1-p)-v.
\]
The three outcomes have distinct logical meanings:
\[
\text{certified feasible}\iff \forall (p,v)\in B,\ g(p,v)\ge0;
\]
\[
\text{certified infeasible}\iff \forall (p,v)\in B,\ g(p,v)<0;
\]
\[
\text{unresolved otherwise.}
\]
The first statement is universal feasibility, not merely the existence of a feasible point. The second is universal exclusion, not merely a negative nominal margin. A box containing both feasible and infeasible points must remain unresolved.

## 338 — Why the endpoint formula is complete

For fixed \(v\), the function \(p\mapsto p(1-p)-v\) is concave, with derivative \(1-2p\) and second derivative \(-2\). Therefore its minimum on a closed interval occurs at an endpoint, and its maximum occurs at \(p=1/2\) if that point lies in the interval, otherwise at an endpoint. Since \(g\) decreases monotonically with \(v\),
\[
g_{\min}=\min\{p_-(1-p_-),p_+(1-p_+)\}-v_+,
\]
\[
g_{\max}=\max_{p\in[p_-,p_+]}p(1-p)-v_-.
\]
Thus \(g_{\min}\ge0\) proves universal feasibility; \(g_{\max}<0\) proves universal infeasibility. The strict inequality in the second condition matters.

## 339 — Boundary logic is asymmetric by necessity

If \(g_{\min}=0\), every point still satisfies the non-strict constraint, so feasibility is certified. If \(g_{\max}=0\) but \(g_{\min}<0\), at least one point may satisfy the constraint while others do not; the correct classification is unresolved. Treating \(g_{\max}=0\) as infeasible would confuse “no strictly positive margin” with “no feasible point.”

## 340 — Exact arithmetic has a precise scope

Using rational arithmetic over each input's decimal-string representation removes floating-point rounding from interval endpoints and margin comparisons. The certificate is exact relative to those represented inputs and the declared box model. It does not validate whether measurements, uncertainty bounds, independence assumptions, or the probability interpretation are empirically justified. Arithmetic exactness is not model validity.

## 341 — Regression extension

The candidate adds tests for (i) a box whose interval lies wholly below or above the maximizer \(p=1/2\), and (ii) the knife-edge \(g_{\max}=0\) case. These target two failure modes: using \(1/4\) as the maximum even when \(1/2\notin[p_-,p_+]\), and misclassifying equality at the upper margin. **These new committed tests have not yet been run in the full repository or on a hosted runner.**

## 342 — Great Scale mapping without semantic substitution

The existing project convention remains
\[
\Psi=\mathrm{CONE}+S,\qquad S=h(1-h),\qquad \mathrm{CONE}=\phi^{-2}.
\]
The certificate uses a separate model \(g(p,v)=p(1-p)-v\). The shared quadratic shape does not establish that \(p=h\), \(v\) is a Great Scale physical observable, or that the certificate proves a statement about \(\Psi\). Such a bridge requires explicit definitions, units/domains where applicable, and a separate derivation. The provisional relation \(\Psi=H-\sigma\) also remains distinct.

## 343 — Cross-domain implication: preserve quantifiers and identity

The same evidence error appears in different forms: a nominal point is mistaken for an uncertainty-set guarantee; a simulation output is detached from its RNG and initial state; a short identifier is mistaken for a unique identity; or a green result from one revision is attributed to another. In each case, a claim has lost a binding condition. Reliable transfer requires preserving both **what is claimed** and **the quantifiers, assumptions, identity, and history under which it is claimed**.

## 344 — Profound finding: certainty is a relation, not a property of a number

A scalar result does not carry its own epistemic status. “Feasible,” “verified,” and “authorized” are relations between a claim and a declared domain, model, execution, evidence record, and decision rule. The same numeric value can support different conclusions under different uncertainty sets; the same passing test can support different conclusions when attached to different commits or models.

For Great Scale, the governing discipline is therefore:
\[
\operatorname{ClaimValid}(c)\Rightarrow
\operatorname{Domain}(c)\land\operatorname{Model}(c)\land
\operatorname{EvidenceBound}(c)\land\operatorname{RuleSatisfied}(c).
\]
This is a proposed epistemic/engineering contract, not a new physical law and not yet an end-to-end enforced repository invariant. The candidate remains draft until required tests execute on the exact reviewed revision with retrievable run evidence and receipt.
