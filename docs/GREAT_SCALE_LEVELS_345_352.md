# Great Scale Descent XII — Replay, authorization, and evidence-bound transitions (Levels 345–352)

**Status labels:** Levels 345–348 are formal engineering models derived from the inspected source patterns; Levels 349–352 are proposed contracts and research conclusions. These are not claims of new physical laws. Cross-repository observations refer to source snapshots reviewed for this descent.

## 345 — A simulation path is a function of more than its visible state

A stochastic simulation should be modeled as
\[
x_{t+1}=F_{v,\theta}(x_t,r_t),
\]
where \(x_t\) is the complete state, \(v\) is the transition-code version, \(\theta\) is configuration, and \(r_t\) is the explicit random input consumed at step \(t\). A replay claim requires the same initial state, configuration, code/runtime contract, event ordering, and random-input stream. A seed alone is not a complete replay contract if PRNG algorithms, stream allocation, or iteration order can change.

**Source observation:** CycleKernal's simulation core uses NumPy's global random functions for faction selection and drift and also records wall-clock timestamps. This makes an exact historical trajectory depend on implicit process state and runtime context. Issue #2 already tracks replayability; this level sharpens the contract rather than claiming the issue is resolved.

## 346 — A probability score and an authorization decision are different types

Let \(s\in[0,1]\) be an advisory score and \(a\) be an authorization decision. A policy may use \(s\) as evidence, but \(s\) is not itself an authenticated principal or a cryptographic approval:
\[
\operatorname{Score}(e)=s\quad\not\Rightarrow\quad
\operatorname{Authorized}(u,d,p).
\]
Here \(u\) is an approver identity, \(d\) is the exact proposed diff, and \(p\) is the policy version. The authorization predicate must independently validate identity, permission, signature, and binding to the reviewed diff.

**Source observation:** TrainLLM's inspected proposal path generates random trust/counterfactual scores and can approve based on a score threshold; the default signature argument is the literal string `mock_human`. This is a source-level control-design risk, not evidence that a production deployment was exploited. Existing TrainLLM issue #3 records the authorization concern.

## 347 — Bind approval to the object that was reviewed

A robust approval record should bind at least
\[
A=(h(d),u,\operatorname{sig},p,\operatorname{decision},t),
\]
where \(h(d)\) is a collision-resistant digest of the exact canonical diff, \(u\) is the authenticated approver, \(\operatorname{sig}\) is a verified signature, \(p\) is a versioned policy, and \(t\) is the audit timestamp. Any mutation of \(d\) invalidates the prior approval. A free-form string or a score threshold cannot substitute for this binding.

This is a proposed authorization contract, not a claim that the current TrainLLM implementation already enforces it.

## 348 — Replay receipts and approval receipts answer different questions

A replay receipt asks: “Can this transition be reproduced from its declared inputs?” An approval receipt asks: “Was this exact change authorized under the policy that applied?” A test receipt asks: “Did these specified checks execute against this revision, and what were their results?” None implies either of the others:
\[
\operatorname{Replayable}\not\Rightarrow\operatorname{Authorized},\qquad
\operatorname{Authorized}\not\Rightarrow\operatorname{Correct},\qquad
\operatorname{TestsPassed}\not\Rightarrow\operatorname{Authorized}.
\]
A complete release gate composes these predicates instead of collapsing them into one green status.

## 349 — Make state transitions explicit and total

For a promotion state machine, define state \(q\in\{\text{candidate},\text{approved},\text{deployed},\text{rejected},\text{superseded}\}\) and a transition relation \(T(q,e,p)\), where \(e\) is evidence and \(p\) is policy. Every permitted transition should state its preconditions, effects, audit event, and rollback behavior. Missing evidence must map to a non-promoting state, not to an implicit success.

The exact lifecycle vocabulary may differ across repositories; a migration must preserve existing semantics and be versioned.

## 350 — A replayable path is not necessarily a valid path

Determinism is necessary for reproducibility, but it does not prove the transition function is sound, the model is empirically valid, or the authorization policy is appropriate. A deterministic implementation can repeatedly produce the same wrong result. Thus the evidence stack needs separate gates for:
1. input/state validity;
2. transition-rule correctness;
3. replayability;
4. policy authorization;
5. empirical/model adequacy where the claim is empirical.

## 351 — Proposed cross-repository evidence contract

Before a high-impact transition is promoted, the evidence envelope should identify:
- repository and immutable code revision;
- canonical input/state hash and configuration version;
- explicit random-stream/seed and PRNG version where stochastic;
- claim and model/domain version;
- tests actually executed, exit statuses, and logs/artifact references;
- approval identity and signature bound to the exact diff, where approval is required;
- decision policy version, transition outcome, and rollback/audit reference.

A missing field should be classified as **unverified** or **not applicable with rationale**, never silently inferred. This contract should be adopted incrementally and tested at each repository boundary.

## 352 — Profound finding: no evidence should be allowed to certify itself

A generated score, a simulation's own assertion, a successful test, or a string named “signature” cannot independently establish every condition needed to trust the object that produced it. Evidence becomes useful only when its provenance, scope, and authority are checked by a distinct verification rule.

\[
\operatorname{Trustworthy}(c)
\Rightarrow
\operatorname{Scoped}(c)\land
\operatorname{Provenanced}(c)\land
\operatorname{IndependentlyChecked}(c)\land
\operatorname{AuthorizedIfRequired}(c).
\]

This is a proposed Great Scale assurance principle, not a new theorem of physics and not yet an end-to-end enforced invariant across all three repositories. It complements Level 344: certainty is relational, and the evidence relation must not be circular. The combined verification PR remains draft until the relevant suites execute on the exact reviewed commit and the resulting receipt is retrievable and bound to that run.
