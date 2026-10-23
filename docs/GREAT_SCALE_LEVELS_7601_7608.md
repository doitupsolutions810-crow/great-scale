# Great Scale — Levels 7601–7608: Bounded Work Is a State-Transition Invariant

**Status:** source-derived software control finding, formal resource-budget contract, and deterministic toy verification. Not a physical or quantum result.

## Level 7601 — Trace the public control path

In CycleKernal `backend/simulation_core.py`, the `POST /simulate/<int:cycles>` route forwards the caller-provided integer to `kernel.run_simulation(cycles)`. That method iterates over the requested number of cycles and over every universe for each cycle. The reviewed module shows no explicit maximum-cycle guard or route-level authorization check. Socket.IO start/stop handlers also show no local authorization check.

Source: [CycleKernal simulation_core.py](https://github.com/doitupsolutions810-crow/CycleKernal/blob/main/backend/simulation_core.py). This is source-level evidence only; deployment reachability, reverse-proxy controls, and upstream middleware were not inspected.

## Level 7602 — Derive a cost model

Let (n) be the requested cycle count and (a_j) the active civilization count in universe (j). A first-order work proxy is

[
W(n) = n sum_{j=1}^{U} a_j.
]

This omits per-civilization computation and instrumentation overhead, so it is a lower-level accounting proxy, not a wall-clock guarantee. If (n) has no enforced upper bound, this model supplies no finite request-level worst-case work bound for fixed nonzero state size.

## Level 7603 — Separate validity, authority, and budget

A safe operation requires all three independent predicates:

[
operatorname{Admissible}(o,p) =
operatorname{Valid}(o)
land operatorname{Authorized}(p,o)
land operatorname{WithinBudget}(p,o).
]

A syntactically valid integer is not necessarily authorized, and an authorized request is not necessarily affordable. None of these predicates implies either of the others.

## Level 7604 — Define a finite budget contract

For a configured limit (N_{max}), require

[
0 le n le N_{max},
qquad
W(n) le B_p,
]

where (B_p) is the applicable per-principal or aggregate work budget. Enforce the bound before mutating state. Also bound concurrency, provide cancellation/deadline behavior, and protect simulation start/stop controls with operator authorization. The actual values of (N_{max}), (B_p), and rate limits are deployment choices and must be measured and documented; this note does not invent production limits.

## Level 7605 — Reject ambiguous no-op success

In the reviewed route, a negative cycle count can reach a Python range loop that performs zero iterations, yet the route can return a success-shaped response containing that negative count. The contract should reject invalid counts explicitly rather than treating “did no work” as successful execution.

## Level 7606 — Falsifiable acceptance conditions

Reject negative and over-limit requests before any state mutation. At the exact configured maximum, verify precisely the allowed number of cycles. Unauthorized callers must not invoke simulation controls. Concurrent calls must not exceed the aggregate budget. Cancellation must terminate cleanly and leave no unintended background task running.

These conditions require tests against the actual app and its real authorization middleware. A toy model cannot establish application security.

## Level 7607 — Deterministic toy checks

A standalone contract model checks these properties: negative count rejected; count above maximum rejected; exact maximum accepted; and unauthenticated control rejected. These are model checks only, not executions of CycleKernal or Great Scale repository tests.

## Level 7608 — Cross-repository integration

Track the source finding in [CycleKernal issue #7](https://github.com/doitupsolutions810-crow/CycleKernal/issues/7). Connect it to Great Scale's existing scheduler-bound work: finite timer delays prevent runaway scheduling cadence, while finite operation budgets prevent runaway work per invocation. Both are instances of the same higher-level contract:

[
	ext{Externally triggered transition}
Rightarrow
	ext{authorized} land 	ext{domain-valid} land 	ext{resource-bounded}.
]

**Profound engineering finding:** a transition is not operationally safe merely because its mathematics is valid. The transition must also be authorized and have a finite, enforceable cost envelope. Domain validity, authority, and resource boundedness are orthogonal proof obligations.

## Verification boundary

- Source observation: confirmed from the fetched CycleKernal file.
- Toy assertions: reported separately from application tests.
- Actual CycleKernal tests, integration tests, CI run, and deployment build: not executed or verified in this review.
- No CycleKernal runtime code was changed. The Great Scale document is a research candidate on a new branch; it does not alter production behavior.
