# Great Scale — Levels 8313–8324: concurrent transitions and linearizable state

## Finding and epistemic status

**Source observation:** both CycleKernal and TrainLLM expose shared mutable simulation state to more than one execution path. In CycleKernal, \`ChatMemoryBridge.process_interaction()\` performs read–modify–write updates to a civilization record while \`background_simulation()\` / \`CycleKernel.run_simulation()\` can update the same records; the HTTP \`/simulate/<cycles>\` route can also invoke simulation directly. In TrainLLM, \`simulation_loop()\` runs in a background \`threading.Thread\`, while \`/chat\` calls \`memory_bridge.process_interaction()\` against the same shared universe objects. The inspected methods do not establish a common lock, transaction, or serialized command queue around these mutations.

This is a **source-level race condition risk**, not evidence that a production deployment was reached, that a race has been observed in a live system, or that a particular request schedule is guaranteed under every deployment/runtime configuration. Upstream process topology, server workers, and deployment middleware were not inspected.

## Mathematics: linearizability of state transitions

Let state be \`x\`, and let one interaction update attention by

\`T(x) = min(150, x + 10)\`.

For \`x = 50\`, two accepted interactions serialized in either order produce \`T(T(50)) = 70\`.

But a read–modify–write interleaving can be:

1. Request A reads \`x = 50\`.
2. Request B reads \`x = 50\`.
3. A writes \`min(150, 50 + 10) = 60\`.
4. B writes \`min(150, 50 + 10) = 60\`.

The final state is 60, not 70. Because both sequential orderings yield 70, the observed interleaving is not equivalent to any serial ordering of these two accepted operations. If both interactions are also appended to the audit log as +10 events, the event history claims +20 of attention deltas while the state changed by only +10.

**Derived criterion:** for every concurrent history \`H\` of accepted transitions, there must exist a legal sequential history \`S\` that preserves real-time precedence and has the same externally observable result. This is the linearizability contract for state mutation. Where strict linearizability is unnecessary, the system must still specify a weaker consistency model and reconcile event history with resulting state.

## Great Scale mapping

| Level | Mathematics | Science / engineering interpretation | Test / verification gate |
|---|---|---|---|
| 8313 | Model each request as a state transition \`T_i : X → X\` | HTTP, socket, and background work share one state space | Enumerate every writer |
| 8314 | Sequential result \`T(T(50)) = 70\` | Two +10 interactions should both be reflected | Sequential baseline |
| 8315 | Interleaved read–modify–write can end at 60 | A race loses one accepted update | Deterministic schedule counterexample |
| 8316 | \`60 ∉ {T_A∘T_B(50), T_B∘T_A(50)}\` | The outcome is not equivalent to a serial ordering | Linearizability check |
| 8317 | Event sum \`ΣΔattention = 20\`, state delta \`=10\` | Audit history and materialized state can disagree | Reconcile event ledger with state |
| 8318 | Shared state must have an explicit serialization boundary | A per-route lock is insufficient if other writers bypass it | Writer inventory and common lock/queue review |
| 8319 | State update and audit append need a defined atomicity contract | A crash or interleaving must not commit only half a logical event | Fault-injection test |
| 8320 | Idempotency key \`k\` should make retries satisfy \`Apply(k); Apply(k) ≡ Apply(k)\` | Network retries must not double-apply a logical command | Duplicate-command replay test |
| 8321 | Snapshot reads need a consistent cut across related fields | Clients must not observe impossible mixtures of old and new state | Concurrent snapshot invariant test |
| 8322 | Randomness, event order, and command IDs belong in replay metadata | Reproducibility requires more than storing a seed | Deterministic replay receipt |
| 8323 | A serializable transaction, actor queue, or correctly scoped lock can establish an ordering | Choose one state-ownership model and enforce it for every writer | Cross-entry-point integration test |
| 8324 | Correct local transition rules do not imply correct concurrent composition | Global correctness requires transition atomicity and a consistency contract | Exact-head stress, integration, and replay tests |

## Deterministic toy test

The toy test checks the mathematics only:

- Sequential A then B yields 70.
- Sequential B then A yields 70.
- The explicit interleaving yields 60.
- The interleaved result differs from both legal serial orders.
- Two +10 audit entries paired with a +10 state delta fail ledger reconciliation.

The toy model does not import or execute CycleKernal or TrainLLM, and it does not demonstrate that a live race occurred.

## Integration plan

1. **Choose a state ownership model:** a single-writer actor/queue, a lock covering the complete logical transition, or a transactional store with suitable isolation. A lock must be shared by all writers to the same object; separate per-route locks do not suffice.
2. **Commit state and event together:** persist the mutation and its event/command receipt atomically, or use a transactional outbox/event-sourcing design with explicit recovery.
3. **Add idempotency:** bind a stable command ID to the authenticated principal and operation; reject or replay duplicate IDs rather than applying the mutation twice.
4. **Protect snapshots:** take snapshots under the same synchronization boundary or read from a versioned immutable snapshot.
5. **Replay:** record transition ID, principal, prior-state version, policy/version, inputs, RNG stream/state where relevant, resulting-state version, and outcome.
6. **Regression gates:** concurrent same-user updates, simulation/chat overlap, duplicate retries, crash between state and audit writes, and snapshot consistency. Run these against the actual repository and deployed concurrency model.

## Profound finding

**A transition can be locally correct and still be globally incorrect when concurrent composition is not serializable.** State sufficiency (previous levels) answers whether a transition receives enough information; linearizability answers whether competing transitions are applied as a coherent history. Great Scale therefore needs both a *state-sufficiency gate* and a *concurrent-history gate*. This is a software systems result, not a claim about physical quantum coherence.

## Verification boundary

The source review is based on CycleKernal \`backend/simulation_core.py\` blob \`5bf4dec4db280e3ec968ceb5d7767923f28d0c8a\` and TrainLLM \`full_cyclekernel_buildA_FH_complete.py\` blob \`169b8b1737aaa73583589d142fa3d6676b33f221\`. The deterministic interleaving test is a standalone model. Repository test suites, threaded stress tests, integration tests, deployment topology, and production behavior remain unverified. Do not merge or deploy based on the toy test alone.
