# Great Scale — Levels 385–392: Authorization Must Survive Every Channel

**Status:** source-level security observation, formalized information-flow invariant, and proposed test contract. Reviewed source: CycleKernal backend/simulation_core.py on main. This is a software-security result, not a physical quantum claim.

## Level 385 — Trace every output channel

The inspected module exposes GET /state returning the complete kernel state; GET /chat/context/<user_id> accepting the lookup identity in the path; and a chat interaction path that emits a Socket.IO event containing a full civ_state without a recipient room. Simulation start/stop socket handlers have no visible authorization check in this file. CORS and Socket.IO origin permissiveness are also present. These are source observations; upstream middleware, deployment reachability, and live exploitability remain unverified.

## Level 386 — Define noninterference

**Definition (security noninterference):** for principals A and B, changing A's private state while holding B's authorized inputs fixed must not change any output observable by B, except for explicitly declassified public aggregates.

Let states s and s' differ only in A-private data, and let Obs_B denote all HTTP responses, WebSocket events, and control effects observable by B. The desired property is:

Obs_B(s) = Obs_B(s') whenever s and s' are equivalent with respect to B's authorized view.

The equivalence intentionally ignores A-private fields but preserves B's state and approved public aggregates.

## Level 387 — Why route-local checks are insufficient

**Derived architectural result:** access control is a property of the complete observation graph, not a single endpoint. Even if a memory lookup route is fixed, a global event broadcast containing the same record can reintroduce the disclosure. The protection boundary must cover HTTP reads, mutations, Socket.IO delivery, telemetry, logs, and administrative controls.

## Level 388 — Separate authentication, authorization, and minimization

For request e, resource r, action a, and principal p:

Permit(e,r,a) = Authenticated(p) AND Authorize(p,r,a)

For event delivery to session q:

Deliver(event,q) implies Authorized(q,event.resource) AND Minimized(event.payload)

Authentication establishes who the caller is; authorization decides what they may do; minimization limits what the channel discloses. None substitutes for the others.

## Level 389 — Cross-channel threat model

The critical paths to test together are: (1) HTTP aggregate state and user-specific context endpoints; (2) chat mutation and simulation cycle controls; (3) WebSocket event delivery and start/stop commands; (4) telemetry, logs, and status endpoints. A passing test for one path does not establish noninterference across the remaining channels.

## Level 390 — Deterministic two-principal regression

Construct principals A and B with distinct private sentinel values. Trigger a mutation for A. Assert that A can observe the authorized update, B receives no A-private sentinel in any response/event, and public aggregates contain only documented declassified fields. Repeat with no principal, wrong principal, expired credentials, and operator-only controls.

This is a test specification, not a claim that the live repository test suite has run.

## Level 391 — Receipt contract

A verification receipt should bind: source commit, policy version, test suite/version, principal roles, test fixture identifiers (pseudonymous), channels exercised, assertion outcomes, and artifact hashes. Do not include raw credentials or private payloads in the receipt. Replay should use deterministic fixtures and record any nondeterministic components.

## Level 392 — Falsification gate

**Falsifier:** any request or event lets B observe A-private state, or lets a non-operator alter shared simulation state, without an explicit grant.

**Acceptance gate:** all HTTP, WebSocket, and telemetry regressions pass against the actual app plus deployment-equivalent auth middleware; the exact commit is identified; and a same-run receipt is retrievable and verifiable. A source edit or a CI status with no runner logs is not sufficient.

**Epistemic label:** the code paths above are source-level observations. The noninterference property is a formal security requirement. Live exploitability and remediation effectiveness are unresolved until integration tests and deployment review pass.