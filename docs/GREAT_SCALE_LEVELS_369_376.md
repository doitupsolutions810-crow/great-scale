# Great Scale — Levels 369–376: Confidence Is Not Authority

**Status:** derived control-flow analysis + proposed invariant; not a claim about physical quantum systems. Source reviewed: `doitupsolutions810-crow/TrainLLM`, default-branch `full_cyclekernel_buildA_FH_complete.py` (source blob observed during review). Related finding: [TrainLLM issue #4](https://github.com/doitupsolutions810-crow/TrainLLM/issues/4).

## Level 369 — Separate evidence from authority

Let a proposal be `q`, its heuristic confidence be `c(q) ∈ [0,1]`, and its authorization evidence be `a(q)`. Confidence is a model output; authorization is a policy decision verified against an authenticated principal and a specific action. They have different types and must not share a coercion path.

**Definition:** `Confidence(q)` is evidence for prioritization or review. `Authorized(q)` is true only when a verifier accepts a scoped, fresh, authenticated authorization bound to the proposal's canonical content.

## Level 370 — Source-derived control-flow result

The reviewed TrainLLM source samples `trust_score` from `random.uniform(0.6, 0.95)`, samples counterfactual trust from `random.uniform(0.7, 0.95)`, and defines approval as:

`counterfactual_trust > 0.8 OR signature == "manual_approval"`

The function's default signature is the literal `"mock_human"`. The simulation loop calls approval automatically when `trust_score > 0.92`, using that default argument. Thus the automatic branch does not establish human identity or cryptographic authorization.

Assuming the sampled values are uniform on the stated intervals, conditional on the automatic-call threshold being met:

\[
P(\text{trust predicate}) = \frac{0.95-0.8}{0.95-0.7}=0.6.
\]

The automatic-call threshold itself has probability:

\[
P(\text{trust\_score}>0.92)=\frac{0.95-0.92}{0.95-0.6}=\frac{3}{35}\approx0.0857.
\]

Under independence of the two random draws, the probability of both thresholds passing for a proposal is approximately \(\frac{3}{35}\cdot0.6=\frac{9}{175}\approx0.0514\). This is a probability implied by the sampling model, not an observed runtime rate. The important defect does not depend on the numeric probability: a heuristic score is being used as authority.

## Level 371 — Typed transition invariant

Use a lifecycle `candidate → approved → applied`, with explicit transition guards. The core invariant is:

\[
\operatorname{Approved}(q)\Rightarrow \operatorname{Candidate}(q)\land\operatorname{Verify}(a,\operatorname{hash}(q),\operatorname{scope}(q),\operatorname{nonce}(q),\operatorname{expiry}(q)).
\]

And the non-implication is mandatory:

\[
\forall c\in[0,1],\quad c(q)=c\;\not\Rightarrow\;\operatorname{Approved}(q).
\]

No confidence value, including 1, may by itself satisfy the authorization guard.

## Level 372 — Bind the authorization to exact content

An approval must bind at minimum to proposal ID, canonical diff hash, repository/model revision, allowed action scope, authenticated principal, expiry, and a replay-protected nonce. If the diff changes after approval, its hash changes and the approval must no longer authorize it.

## Level 373 — Verify at both boundaries

Check the guard when transitioning `candidate → approved` **and again** when moving `approved → applied`. The second check protects against queue tampering, stale approval, wrong-target application, and replay. Make application idempotent and emit a receipt tying the decision to the exact proposal hash and resulting state revision.

## Level 374 — Deterministic regression matrix

The following tests are required before promotion; they are proposed tests, not executed tests in this document:

1. `trust_score=1.0` and counterfactual trust `=1.0` with no authorization ⇒ remains candidate / denied.
2. Missing, default, malformed, or forged signature ⇒ denied.
3. Valid authorization for hash `h1` cannot approve proposal hash `h2`.
4. Expired authorization and replayed nonce ⇒ denied.
5. Correct principal but insufficient scope ⇒ denied.
6. Valid scoped authorization approves exactly the bound proposal once.
7. An approved proposal changed before application ⇒ application denied.
8. An applied receipt is deterministic under replay of the same event log; duplicate application does not repeat side effects.

## Level 375 — Great Scale relation

Keep this gate separate from the existing Great Scale convention \(\Psi=\mathrm{CONE}+S\), \(S=h(1-h)\), \(\mathrm{CONE}=\phi^{-2}\), and separate from the provisional research quantity \(\Psi=H-\sigma\). Neither expression proves authorization. If a scalar score is included in a governance objective, it remains evidence and cannot replace the typed authority predicate.

A useful audit tuple is:

\[
R=(\text{proposal hash},\text{policy version},\text{principal},\text{scope},\text{nonce},\text{decision},\text{state revision}).
\]

The receipt should be signed or otherwise integrity-protected and should distinguish `not_run`, `failed`, and `passed` verification outcomes.

## Level 376 — Falsification gate and status

**Falsifier:** produce a deterministic execution where a proposal reaches `approved` or `applied` solely because of a confidence value, with no valid scoped authorization. If that trace exists, the invariant is violated.

**Verification status:** source-level defect identified; the lifecycle invariant is mathematically specified; no repository test suite or live deployment was run as part of this analysis. The existing Great Scale integration PR remains a draft until exact-revision tests and receipts are available. This finding does not establish any physical claim about quantum states or dynamics.
