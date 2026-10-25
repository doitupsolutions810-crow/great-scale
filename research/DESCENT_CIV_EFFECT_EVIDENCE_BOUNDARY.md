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
