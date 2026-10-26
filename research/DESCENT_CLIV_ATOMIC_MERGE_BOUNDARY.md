# Descent CLIV — A Final Read Is Not an Atomic Merge Guard

## Finding

CLIII identifies a time-of-check/time-of-use (TOCTOU) boundary. But comparing the latest observed pull-request state to the tested state immediately before merge is still not sufficient if the observation and merge are separate operations. The base can advance after the read and before the merge request is committed.

Thus even this implication is invalid without an atomic or server-enforced condition:

`state_at_final_read == state_at_test  =>  merge_is_safe`

The read establishes equality at one instant, not at the later merge instant.

## Formal model

Let (S(t)) be the relevant review state at time (t), and let (t_c < t_r < t_m) denote test completion, final state read, and merge respectively.

A client-side check proves at most:

`S(t_r) = S(t_c)`

It does not prove:

`S(t_m) = S(t_r)`

because a state transition can occur in ((t_r,t_m)). This is the classic TOCTOU gap.

## Required control

The final acceptance condition must be enforced at the operation boundary, not only by a client-side observation. Use server-enforced required checks and, where appropriate, a merge queue that revalidates changes against the latest base. Pin the expected head SHA for the merge operation where supported. A client-side equality check remains useful for diagnostics, but is not a concurrency control.

## Great Scale mapping

- **State geometry:** (S=(H,B,W,M)).
- **Observation:** read the current state at (t_r).
- **Race window:** ((t_r,t_m)).
- **Invariant required:** merge only if the server guarantees that the accepted candidate is the one covered by required checks.
- **Safe decision:** server-enforced merge policy/queue, not a final read alone.

## Test plan

A model test should show that a matching final read passes a local predicate but cannot guarantee merge safety when a state transition occurs before the merge. A second test should require an explicit server-enforced precondition/queue authorization before the model returns safe.

## Verification status

This is a documented concurrency invariant. It does not assert that repository branch protection, required checks, or merge queue settings have been inspected or enabled. Those settings must be queried and verified independently. No build, full suite, or hosted CI pass is claimed for this note.
