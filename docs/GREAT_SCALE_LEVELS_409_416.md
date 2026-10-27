# Great Scale — Levels 409–416: State Is a Consistency Relation

**Status:** research deduction from inspected source; not a claim about quantum physics.  
**Scope:** CycleKernal `backend/ns_fusion.py` and `backend/simulation_core.py`, with the Great Scale verification/provenance contract.

## Level 409 — One logical state, multiple stored representations

The simulation stores promotion status in at least two fields:

- Boolean: `civ["promoted"]`
- Categorical: `civ["state"]`, including `"active"` and `"promoted"`

These fields are updated together on normal promotion/demotion paths, but they are not represented by one canonical state type or guarded by a consistency assertion in the inspected source.

**Classification:** source observation.

## Level 410 — Define the consistency invariant

Let (b\in\{0,1\}) be the boolean flag and (q\in\{\text{active},\text{promoted},\text{dormant}\}) the categorical state. For the two live states, define:

[
I(b,q)\equiv (b=1\iff q=\text{promoted}).
]

If the design intends `promoted` to be exactly equivalent to state `"promoted"`, then (I) must hold at every externally observable boundary—not only immediately after a normal transition.

**Classification:** proposed invariant, conditional on the intended semantics.

## Level 411 — The transition and observation paths use different coordinates

The inspected simulation loop:

1. admits a civilization for processing based on `state in ("active", "promoted")`;
2. chooses promote/demote behavior using the Boolean `promoted`;
3. updates both fields only when the decision is promote or demote.

The snapshot counts promoted civilizations using the Boolean field, while its active count uses the categorical state. Thus an inconsistent pair can produce different answers to “is this civilization promoted?” depending on the observer.

**Classification:** source-level control/data-flow observation.

## Level 412 — Minimal counterexamples

| Boolean (b) | Categorical (q) | Invariant (I) | Observable consequence |
|---:|---|---|---|
| 0 | active | true | Consistent unpromoted state |
| 1 | promoted | true | Consistent promoted state |
| 1 | active | false | Counted promoted by flag; categorized active by state |
| 0 | promoted | false | Not counted promoted by flag; categorized promoted by state |

The last two rows are logically representable by the current data shape. Their reachability from every deployed entry point has not been established; they are valid fault-injection cases regardless.

## Level 413 — Deterministic transition test

For score (s=0.10), demotion threshold (d=0.28), and a decision function that trusts (b):

- Input ((b=1,q=\text{active},s=0.10)) yields a demotion decision from the Boolean flag.
- Input ((b=0,q=\text{promoted},s=0.10)) yields hold from the Boolean flag, leaving the categorical field potentially promoted if the caller only applies the decision result.

The score is identical; the stored representation changes the result. A safe implementation must either reject inconsistent input, normalize through one authoritative state, or explicitly define recovery semantics.

**Classification:** derived counterexample from the source transition contract; not a repository test run.

## Level 414 — State must be atomic at the transition boundary

Define a transition as:

[
T:(x,q,r)\mapsto(x',q',r')
]

where (x) is the entity identity, (q) is the prior logical state, and (r) is the evidence/policy revision. The transition should commit the canonical state and its projections as one logical operation, with an invariant check before publication.

A useful acceptance property is:

[
\forall e\in E_{\mathrm{accepted}},\quad I(e.b,e.q)\land
\operatorname{EvidenceBound}(e)\land
\operatorname{PolicyBound}(e).
]

This is an assurance contract, not a claim that the current runtime already enforces it.

## Level 415 — Verification matrix

Minimum tests to add at the owning repository:

1. Every allowed canonical state maps to exactly one valid projection.
2. Both inconsistent pairs are rejected or repaired by a documented deterministic rule.
3. Promotion and demotion update all projections atomically.
4. Snapshot counts agree with the canonical state.
5. Replay of the same prior state, score, policy revision, and evidence yields the same next state.
6. Invalid or stale evidence cannot mutate state.
7. The test receipt binds the tested commit, policy revision, and test suite.

These tests are specified here; the live CycleKernal suite has not been executed in this environment.

## Level 416 — Profound finding: state is not a scalar

**Finding:** operational state is a consistency relation among identity, canonical state, derived projections, evidence, and policy revision—not a single score or flag.

A local field can be individually well-formed while the global object is invalid. Likewise, a local test can pass while the integrated transition is invalid if the test omits a projection or fails to bind its evidence to the actual revision.

The Great Scale assurance condition is therefore relational:

[
\operatorname{Valid}(e)\iff
\operatorname{IdentityBound}(e)\land
\operatorname{StateConsistent}(e)\land
\operatorname{EvidenceBound}(e)\land
\operatorname{PolicyBound}(e)\land
\operatorname{RevisionBound}(e).
]

This is a systems-engineering deduction from the inspected repositories. It does **not** establish a new physical law, quantum coherence theorem, or empirical claim.

## Verification record

- Source files inspected: CycleKernal `backend/ns_fusion.py` and `backend/simulation_core.py`.
- The source contains separate promotion fields and the transition/snapshot paths read them differently.
- The table and counterexample are deterministic logical checks.
- No CycleKernal integration test, hosted workflow, or deployment was verified during this analysis.
- Follow-up: implement one canonical state representation or a typed transition object in CycleKernal, add fault-injection and snapshot-consistency tests, and attach a same-revision execution receipt before promoting the fix.
