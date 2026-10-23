# Great Scale — Levels 401–408: A Decision Is a Bound Transition

**Status:** the state-machine equations below are derived from the stated threshold policy; repository examples are source-level observations; the cross-system invariant is a proposed engineering contract. This is not a physical claim.

## Level 401 — Scores do not define state transitions alone

Let the persistent state be m in {0,1}, where 0 means unpromoted and 1 means promoted. Let s in [0,1] be a score, with demotion threshold d = 0.28 and promotion threshold p = 0.62. The intended transition is:

T(m,s) = 0 if m=1 and s<d;
T(m,s) = 1 if m=0 and s>=p;
T(m,s) = m otherwise.

The score is an input to the transition; it is not a substitute for the prior state.

## Level 402 — Derive the hysteresis band

Since d < p, every score s in [d,p) preserves either prior state: T(0,s)=0 and T(1,s)=1. This is hysteresis. It prevents a single threshold from making state oscillate whenever noisy scores hover around one boundary.

Boundary contract:
- m=1, s=d: remain promoted because demotion is strict (s<d).
- m=0, s=p: promote because promotion is inclusive (s>=p).
- m=1, s<d: demote.
- m=0, s>=p: promote.

These statements follow from the piecewise definition; they are not empirical claims about the best thresholds.

## Level 403 — A source-level counterexample

In CycleKernal `backend/ns_fusion.py`, `apply_fusion()` originally passed `already_promoted = promoted and fused >= PROMOTE_THRESHOLD`. For a persisted promoted colony whose current score falls below the promotion threshold, this expression evaluates false before the transition function can inspect the demotion threshold. A low score such as 0.0525 is therefore treated as unpromoted and yields hold rather than demote.

A draft correction in CycleKernal PR #4 passes the persisted promotion state directly. The focused arithmetic reproduction is not a run of the actual repository test suite; the PR remains draft pending execution evidence.

## Level 404 — State-transition consistency

A transition is well-defined only relative to a versioned prior state and policy. The minimum transition record is:

`(object_id, prior_state, input_score, policy_revision, next_state, evidence_id)`

A transition log that stores only `score -> action` cannot independently establish whether demotion was eligible, whether promotion was authorized, or whether the action used the intended policy version.

## Level 405 — Compose identity and authorization

For a protected transition q, propose:

[
Apply(q) Rightarrow Auth(principal, object, action, scope, nonce, expiry)
land Unique(object, principal)
land Valid(priorState, policyRevision)
land EvidenceBound(evidence, q).
]

Each predicate guards a different failure class. Authentication does not imply unique storage identity; a unique object key does not imply action authorization; a valid score does not imply permission; and a receipt does not prove that the intended transition was executed.

## Level 406 — Verification receipts must distinguish tested objects

A pull-request workflow may test a synthetic merge commit, while a push workflow tests the branch head. Both can be useful, but their SHAs are not interchangeable. A receipt must separately record:
- checkout SHA actually executed;
- candidate/head SHA being evaluated;
- pull-request base SHA when applicable;
- event type and platform run identity;
- per-suite outcome and same-run artifact identity.

The combined candidate now records checkout and candidate/head metadata separately in `scripts/verify-local.sh` and passes PR head/base SHA metadata from `.github/workflows/ci.yml`. This source change is not yet verified by a successful hosted run.

## Level 407 — Test and falsification matrix

Required transition regressions:
1. promoted + score below 0.28 -> demote;
2. promoted + score exactly 0.28 -> hold;
3. unpromoted + score exactly 0.62 -> promote;
4. unpromoted + score below 0.62 -> hold;
5. a score change alone cannot rewrite the recorded prior state;
6. authorization for object A cannot apply to object B;
7. evidence for revision r cannot certify revision r+1;
8. receipt checkout SHA and candidate SHA must match the expected event semantics.

These are acceptance tests, not claims that the integrated repositories have passed them.

## Level 408 — Profound finding: validity is relational

A number is not a decision. A principal is not a storage key. A passing test is not evidence for every revision. A receipt is not authorization. Each becomes meaningful only through its binding to the relevant object, prior state, policy, code revision, execution, and authority.

**Great Scale invariant:** every consequential transition must preserve the referential chain

[
(principal, object, priorState, policy, evidence, revision)
longrightarrow
(principal, object, nextState, policy, evidence, revision).
]

If any binding is missing or many-to-one without an explicit rule, individually plausible components can compose into an invalid global result. This is a systems-assurance deduction from the reviewed software patterns—not a new law of quantum geometry.

## Verification ledger

- Algebraic threshold cases: derived from the piecewise transition definition.
- CycleKernal wrapper defect: source-inspected; focused calculation reported; repository test suite unverified.
- Great Scale receipt metadata patch: committed to the draft integration branch; hosted validation unverified.
- Cross-tenant isolation, cryptographic authorization, deterministic replay, and end-to-end CI receipt authenticity: unresolved until integration tests and independent evidence exist.
- Promotion/merge/deployment: blocked pending exact-revision tests, retrievable same-run evidence, review, and authorization.
