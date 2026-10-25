# Descent CIV — The Side-Effect / Evidence Commit Boundary

## Finding

An operation's external effect and its audit/evidence record are two separate state transitions unless the system deliberately makes them atomic or idempotent. If the effect succeeds and evidence persistence fails, the caller cannot safely infer either "nothing happened" or "everything is durably recorded."

Capability Authority's executor currently constructs an `ok` receipt and returns `status: ok`; the HTTP handler then records an `ExecuteReceipt` in the evidence index. These steps are not one transaction. The open PR #4 attempts to return `status: indeterminate` when evidence persistence cannot be confirmed, correctly warning against blind retry. That improves honesty but does not by itself make the external operation exactly-once.

## State model

Let:
- (X): the intended side effect occurred;
- (D): the evidence record was durably committed;
- (R): the caller received a response.

The dangerous partial state is:

[
X=1,quad D=0
]

The effect may have happened, while the durable audit record is absent or unknown. A crash can also occur after the effect but before the caller receives a response, leaving the caller unable to distinguish that state from a request that never reached the effect.

A plain retry can then duplicate the effect. Conversely, refusing every retry can leave an operation permanently incomplete. A response field such as `indeterminate` is an honest report of uncertainty, not a transaction protocol.

## Theorem-like engineering statement

Without at least one of:
1. a transaction spanning the side effect and evidence commit;
2. a receiver-enforced idempotency key that returns the original result for repeated requests; or
3. a durable intent/outbox protocol plus idempotent effect application and reconciliation,

a caller-visible exactly-once guarantee cannot be derived from a request/response API alone.

This is an engineering result under crash/failure assumptions, not a physical law.

## Safer protocol

Use a caller-supplied or server-issued immutable `operation_id` bound to the authenticated principal, capability ID, canonical action (including method/resource), and request digest.

1. Atomically persist an intent with unique `operation_id` before initiating the effect.
2. Dispatch the effect using the same idempotency key.
3. Persist the observed outcome and signed receipt against that operation ID.
4. On duplicate delivery, return the recorded outcome or reconcile an in-progress/unknown operation; do not blindly repeat a non-idempotent effect.
5. Mark the operation `indeterminate` if outcome cannot be established, and provide a reconciliation path.
6. Keep evidence-persistence status distinct from effect status.

Suggested lifecycle:
[
mathrm{NEW}	omathrm{INTENT_DURABLE}	omathrm{EFFECT_CONFIRMED}	omathrm{EVIDENCE_DURABLE}	omathrm{COMPLETE}
]
Failure after effect but before evidence commit enters `INDETERMINATE`, not `FAILED_NO_EFFECT`.

## Executable state-space check

`test_effect_evidence_boundary.py` enumerates all combinations of effect outcome known/occurred, evidence durability, and caller response. It asserts the key safety property: if the effect may have occurred but evidence is not durable, the outcome cannot be labeled a clean failure/no-effect and retry must be gated on idempotency or reconciliation.

This finite-state test validates the model only. It does not simulate a real database crash, external effect, broker, or production executor.

## Cross-repository mapping

- **Capability Authority:** separate `Executor.execute()` success from later evidence persistence; PR #4's indeterminate status is a useful first step, not an exactly-once guarantee.
- **Living Intermediate Control Plane:** the durable outbox must use unique operation identity and make duplicate dispatch/replay behavior explicit; a file write or event digest alone is insufficient.
- **CycleKernal:** fusion/promotion lineage identifies computed decisions, but bounded in-memory history is not a durable transactional ledger.
- **Great Scale:** a scalar, digest, or signed receipt describes a state; none alone proves atomic coupling between an external effect and its evidence record.

## Verification status

No repository suite or live side effect was run for this note. The Python test is a finite-state contract test to be run by CI. No claim is made that any current repository implements the complete protocol.


## Source-level refinement — success-status laundering

A follow-up inspection of Capability Authority `main` at `plane_service/server.py` SHA `2cf77b51d1913b4bc3e37df8dadc45739200d276` found a concrete instance of this boundary: `_record_evidence(event)` catches and prints exceptions from both `evidence.index.get_index().ingest(event)` and `BUS.publish(event)`, then returns no status. `handle_execute` calls it after an executor result with `status == "ok"` and returns the original result regardless of whether either evidence path failed.

Thus the API's success response does not establish durable evidence. More precisely, the code does not establish whether the index is durable, whether the bus accepted the event, or whether both failed. This is a code-path finding from the fetched source, not proof of a production incident. The executor source at SHA `e4e3de501d9f0898ff1239b5f2dc010e8c2a82a8` currently constructs a receipt and returns `result: "executed"`; this inspection alone does not prove a real external side effect occurred.

Let `S` mean the API reports success and `D` mean durable evidence exists. The current control flow permits `S = true` while `D = false`, because evidence errors are swallowed. The required contract for an evidence-backed success endpoint is `S => D`: success implies durable evidence.

If the effect may already have happened and (D) cannot be established, the correct response is an explicit indeterminate state plus operation identity and reconciliation—not a clean success and not a claim that no effect occurred.

The existing finite-state test captures the general state distinction. A repository-level regression test should additionally inject failures into both the index and bus and assert that the API never reports evidence-backed completion unless the configured durability contract is satisfied.


## Cross-repository refinement — post-write failure can masquerade as no effect

CycleKernal's default-branch `backend/server.js` at blob SHA `fa16b63e56213fb031624c01b124db900adcb0c3` contains a concrete failure window in `POST /api/chat/save`:

1. `await chatEntry.save()` persists the chat to MongoDB.
2. `countDocuments()` and a Redis `setEx()` run afterward.
3. The handler returns HTTP 500 for any caught error in this sequence.

If MongoDB save succeeds but count or Redis fails, the caller receives an error even though the primary write may already exist. Retrying the request can create a second record because the route does not show a stable idempotency key or uniqueness constraint for an operation identity. The snapshot endpoint also has the generic lost-response ambiguity: persistence can complete before the client learns the result.

Let (W) mean the primary write committed, (A_c) mean the caller received a success acknowledgement, and (R) mean a retry occurs. The implementation admits:

[
W=1 land A_c=0
]

Therefore, the inference (A_c=0 Rightarrow W=0) is invalid. If retry repeats the write without deduplication, duplicate state is possible.

The fix is not merely to change HTTP 500 to HTTP 200. Use a stable operation ID with a database uniqueness constraint or equivalent atomic deduplication, separate primary-write outcome from cache/metrics health, and expose a way to query/reconcile the original operation. Cache failure after a committed primary write should not silently transform a committed write into a retryable no-effect claim.

This is a source-code failure-path analysis, not proof that the deployed service has experienced duplicates. Deployment and runtime fault injection have not been performed.


## Descent CXLI — authoritative ledger versus searchable projection

A second independent failure boundary appears in Capability Authority's evidence pipeline. On default-branch `evidence/index.py` at blob SHA `ada6279eb02fa1286ced2f8c021e5983269cef73`, index initialization catches JSON parse errors and resets `_docs` to an empty list. In `ingest`, exceptions from the hash-chained warehouse append are swallowed; the event is still added to the JSON projection. The corresponding default-branch warehouse at blob SHA `509c1c9ee46f2ca5842b216224c3f5b08a4a74a0` reads the chain tip and appends without acquiring a write lock before the tip read.

The fixes for serialized append, fail-closed index loading, warehouse error propagation, and atomic JSON replacement are proposed in [Capability Authority PR #12](https://github.com/doitupsolutions810-crow/capability-authority/pull/12). The PR is open and unmerged; its controls are not yet the default-branch behavior.

The proposed branch still has a cross-store gap: SQLite commits before the JSON projection is atomically replaced. If SQLite commits and the projection write fails, the ledger and projection diverge. A retry can append the same logical event again unless a stable event ID is enforced by the authoritative store. Atomic replacement prevents partial JSON files; it does not make SQLite plus JSON one transaction.

Let:
- (L): authoritative ledger contains the event;
- (J): searchable projection durably reflects the event;
- (Q): caller receives a success response;
- (K): the authoritative store enforces idempotency for the stable event ID.

The necessary completion condition is:

\[
\operatorname{Complete}=L\land J\land Q
\]

The safe retry condition after a possible ledger commit is:

\[
\operatorname{RetrySafe}=\neg L\lor K
\]

When (L=1) and (J=0), the correct state is `RECONCILE_PROJECTION`, not `FAILED_NO_EFFECT` and not `COMPLETE`. The projection should be rebuildable from the authoritative ledger, and replay should be idempotent by event identity.

The executable model checks all (2^4=16) states. It verifies that completion requires ledger, projection, and acknowledgement, and that retry after a ledger commit requires enforced deduplication. This is a contract test, not a real SQLite/filesystem crash test. Production remediation still needs a stable event ID, unique constraint/migration, replay/rebuild logic, and injected failures after ledger commit but before projection replacement.


## Descent CXLII — stale projection writers can erase each other's events

A further concurrency gap remains in Capability Authority's proposed PR #12. The JSON index uses an instance-local `threading.RLock` and each `EvidenceIndex` instance loads `_docs` into memory at initialization. `_write_atomic` protects readers from seeing a partially written file, but it does not coordinate two processes or two independently initialized index instances.

Counterexample:
1. Process A and process B both load projection state (J_0=[]).
2. A commits event (a) to SQLite and atomically writes (J_A=[a]).
3. B commits event (b) to SQLite and atomically writes its stale-derived (J_B=[b]).
4. The final projection is ([b]), while the authoritative ledger contains both (a) and (b).

The final file is valid JSON and each rename is atomic; nevertheless, event (a) has disappeared from the projection. Thus atomic replacement is not a lost-update solution, and a process-local lock does not establish a cross-process invariant.

Formally, if (L) is the ledger event set and (J) is the projection event set, the required completeness invariant is:

\[
J\subseteq L\quad\land\quad L_{\text{projectable}}\subseteq J
\]

A stale writer can violate the second inclusion even if the first inclusion remains true.

The test extension models this two-writer interleaving and asserts the counterexample: both ledger events exist but the last stale projection omits one. This is a source-grounded concurrency model, not a multiprocess run against the actual SQLite/JSON implementation.

Preferred fixes, in order of simplicity:
1. Make the searchable projection a SQLite table updated in the same transaction as the ledger.
2. Or rebuild the projection from the authoritative ledger under a cross-process coordination/reconciliation protocol.
3. Or use an append-only projection with stable unique event IDs and a reader that tolerates/reconciles duplicate delivery.

A process-local RLock plus atomic file replacement is insufficient. Add an actual multiprocess test that forces the stale-read/write interleaving and then verifies projection completeness against the ledger.


## Descent CXLIII — integrity does not prove completeness

The deeper epistemic limit is that a valid hash chain proves consistency of the records it contains, not that every expected event is present, and not that a separate projection contains every ledger event. Capability Authority's `verify_chain()` walks rows that exist and checks each `prev_digest` and digest. A valid chain of length (n-1) can still be missing an event that should have existed; a valid complete ledger can also coexist with an incomplete JSON projection.

Let (V(L)) mean the stored ledger's chain verifies, and (C(L,J)) mean the projection is complete for the ledger. In general:

\[
V(L)\not\Rightarrow C(L,J)
\]

The stale-writer example gives (L=\{A,B\}), (J=\{B\}), with a valid chain for (L), yet (L\nsubseteq J). Even stronger, a self-consistent chain alone cannot establish that (L) itself includes every event that should have been recorded. Completeness needs an independent expected-event source, sequence/watermark, transactional outbox, or reconciliation against an authoritative producer/operation registry.

The model test now constructs and verifies a two-event hash chain while deliberately omitting one event from the projection. It asserts that chain integrity succeeds while projection completeness fails. This demonstrates the logical separation; it is not a production database integration test.

**Operational implication:** report integrity, completeness, and provenance as separate evidence fields. A single `verified: true` must not imply completeness unless the system also verifies a trusted sequence boundary or reconciles against an independent source of expected events.
