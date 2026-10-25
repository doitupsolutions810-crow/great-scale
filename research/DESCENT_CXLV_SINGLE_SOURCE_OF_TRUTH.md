# Descent CXLV — From replay safety to a single source of truth

## Finding

Capability Authority PR #12 adds stable event identity and serializes ledger appends, but the searchable projection remains a separate JSON file. Its instance-local `threading.RLock` does not coordinate independent processes, and atomic replacement protects file integrity rather than preventing stale-writer lost updates. The source explicitly documents this remaining limitation in `evidence/index.py` on the PR branch.

Two index instances can both load `J₀ = ∅`. Writer A commits event `a` and replaces the projection with `{a}`. Writer B, working from its stale snapshot, commits `b` and replaces the projection with `{b}`. The ledger contains `{a,b}` while the projection contains only `{b}`. Each JSON replacement can be perfectly atomic and the projection can still be incomplete.

## Invariant

Let `L` be the ledger's event IDs and `J` the projection's event IDs. For all projectable ledger events, the required consistency condition is:

\[
J \subseteq L \quad\land\quad L_{projectable} \subseteq J
\]

The second inclusion is the critical completeness property. Stable-ID idempotency prevents duplicate ledger rows; it does not guarantee projection completeness or cross-process consistency.

## Architecture implication

Prefer storing the searchable projection in SQLite and updating ledger plus projection in the same transaction. Use a unique stable event ID in both tables. If the projection is intentionally asynchronous, make it a rebuildable materialized view driven by an outbox/sequence watermark, and expose lag/reconciliation status rather than presenting it as fully current.

A single transaction establishes atomic commit/rollback of the database rows, but it does not establish that the external event source supplied every expected event. Completeness needs an independently trusted expected sequence, producer watermark, signed checkpoint, or reconciliation against the authoritative operation registry. A hash chain can validate retained rows while a valid prefix remains after tail truncation.

## Formal separation

- `Integrity`: retained rows satisfy the hash-chain relation.
- `Identity`: a stable event ID maps to at most one logical payload.
- `Projection consistency`: the projection reflects all projectable ledger rows.
- `Completeness`: the ledger itself reaches an independently trusted expected boundary.
- `Authenticity`: event provenance is tied to a trusted signer/principal.

None of these properties implies all the others. In particular:

\[
Integrity(L) \not\Rightarrow Completeness(L)
\]

and

\[
Integrity(L) \not\Rightarrow ProjectionComplete(L,J)
\]

## Executable check and limits

`test_great_scale_cxlv_atomic_projection.py` checks three model obligations: a single SQLite transaction commits or rolls back ledger and projection rows together; the stale JSON writer interleaving loses an event; and a truncated prefix requires an external expected boundary to detect incompleteness. The test was run locally with Python 3 in an isolated temporary directory: **3/3 checks passed**. This validates the model, not Capability Authority's actual implementation or production deployment.

## Repository integration status

This note and its model test are added to the open Great Scale PR #128 branch. Capability Authority PR #12 remains open and unmerged. Its hosted run `40223320786` has failed `test` and `slim-probe`; job-log retrieval returned unavailable/not-found, and the exact cause is not established. No full repository build, multiprocess integration test against the real implementation, or production verification is claimed.

## Next proof obligation

Implement or prototype the SQLite-backed projection and run tests against the actual warehouse/index classes with two independent processes, forced crashes between write stages, duplicate-ID races, projection rebuild, and externally anchored checkpoint mismatch. The acceptance gate should require both transactional consistency and independent completeness evidence before the system reports fully verified history.
