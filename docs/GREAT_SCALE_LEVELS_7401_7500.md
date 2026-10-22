# Great Scale — Levels 7401–7500: scheduler-domain contracts

## Profound finding

PR #100 closes two state-domain holes, but a separate public input still crosses directly into the runtime scheduler: `DescentEngine({ tickMs })` stores the value and `start()` passes it to `setInterval`. The constructor previously accepted zero, negative, non-finite, and over-limit delays. JavaScript timer implementations coerce or clamp some such values; in Node, values beyond the signed 32-bit timer range can overflow to a very short delay. A bad delay can therefore change the intended cadence or create an unexpectedly hot loop rather than expressing the caller's intended wait.

The scheduling contract is now explicit:

\[
1\ \mathrm{ms}\leq \Delta t\leq 2^{31}-1\ \mathrm{ms},\qquad \Delta t\in\mathbb{R},\quad \Delta t<\infty.
\]

The lower bound avoids zero/negative/sub-millisecond coercion. The upper bound stays within the common signed-32-bit timer range. The guard is applied in the constructor and again in `start()`, because `tickMs` is a public mutable property and constructor-only validation would be bypassable.

## Integration

- Added `validateTickInterval` to the ES-module and CommonJS runtimes.
- Validate timer delays at construction and immediately before scheduling.
- Set `running = true` only after `setInterval` has returned, so a synchronous scheduling failure does not leave a false running flag.
- Added regression tests for zero, negative, non-finite, oversized, and boundary delays, plus post-construction mutation.
- Updated the README runtime contract.

## Great Scale mapping

**Level 7401 — Scheduler preconditions.** A state-transition cadence is part of the runtime contract, not an unvalidated implementation detail.

**Level 7402 — Bounded temporal domain.** Require \(1\leq\Delta t\leq 2^{31}-1\) milliseconds and finite \(\Delta t\).

**Level 7403 — Mutation-resilient validation.** If configuration remains publicly mutable, validate again at the point of use; otherwise make it immutable.

**Level 7404 — Failure-state consistency.** If timer creation fails, the engine must not report itself as running.

## Verification boundary

The source-level failure mode and the guard are inspectable. Regression tests have been added, but the committed repository test suite and hosted build must still be executed against the resulting exact head. This is a software scheduling/resource-control finding, not a claim about quantum physics or experimental science.
