# Operation and Evidence Contract v1

Status: proposed cross-repository contract. The services linked below are candidate implementations; this document does not claim their end-to-end path has passed.

## 1. Core invariant

A request intent, external effect, evidence receipt, and client acknowledgement are distinct state transitions. A successful HTTP response, a valid JSON payload, a hash-chain entry, or a model-generated decision is not sufficient by itself to establish that a production action completed and is authorized.

The acceptance predicate is conjunctive:

```text
Accept(operation) =
    StableOperationIdentity
  AND RequestDigestBound
  AND AuthorizationForExactAction
  AND DurableIntentReadBack
  AND ObservedEffectOutcome
  AND DurableReceiptReadBack
  AND ExactRevisionAndSourceBinding
```

If the effect may have happened but its outcome or receipt cannot be established, return `indeterminate`, preserve the operation ID, and reconcile. Do not claim a clean no-effect failure and do not issue a fresh operation ID to “retry” the same uncertain operation.

## 2. Shared envelope

Every cross-service operation should preserve these logical fields. Language-specific code may use snake_case or camelCase internally, but adapters must map them explicitly rather than silently drop them.

| Field | Meaning |
|---|---|
| `schema_version` | Version of the shared operation/evidence contract. |
| `operation_id` | Stable opaque ID created once for the logical operation and reused across retries and downstream calls. |
| `request_digest` | SHA-256 of this service's canonical, security-relevant request payload, excluding transport headers and the operation ID. |
| `parent_operation_id` | Upstream operation ID when this action is part of another operation. |
| `parent_request_digest` | Digest from the upstream boundary, preserving trace lineage without claiming the local digest must match it. |
| `event_id` | Stable, producer-namespaced ID for one logical lifecycle stage, e.g. intent or receipt. It remains unchanged on duplicate delivery. |
| `stage` | `intent`, `receipt`, or `reconciliation`. |
| `decision_state` | `pending`, `completed`, `indeterminate`, `conflict`, or `denied`. |
| `producer.repository` | Exact repository that emitted the evidence. |
| `producer.commit_sha` | Full 40-character source revision associated with the producer. |
| `observed_at` | Timestamp of the observation, not an inferred execution time. |
| `evidence_ref` | Durable receipt, workflow/job run, or immutable artifact reference. |
| `authority_ref` | Capability/approval identifier and method/resource scope for actions that require authority. |

Each service computes its own `request_digest` over the request it is responsible for. Digests from different service boundaries are not expected to match if their payloads differ. The upstream digest is carried separately in `parent_request_digest` for correlation.

## 3. Lifecycle and retry rules

1. **Validate identity.** Require a non-empty bounded operation ID; reject re-use with a different request digest.
2. **Persist intent.** Append the intent to durable storage and read it back before invoking the side effect.
3. **Authorize.** Check capability/approval against the exact action, including resource and method. Availability, a local fallback, or an agent-generated command is not authority.
4. **Execute once per operation identity.** The downstream system must receive the same operation ID/idempotency key if it can cause a side effect.
5. **Persist and read back the receipt.** The receipt binds the operation ID, request digest, action, observed outcome, producer/revision and any applicable cryptographic verification result.
6. **Reconcile uncertainty.** A repeated operation ID with a completed durable receipt returns the original result. A conflicting payload is rejected. An in-progress or indeterminate operation without a receipt is not automatically re-executed.
7. **Report semantics honestly.** A confirmed primary write can return success with ancillary cache/metrics degraded. A result whose primary outcome is not known remains indeterminate.
8. **Promote only exact evidence.** Tests must be executed on the exact candidate SHA, and run/job outcomes must be observed. A workflow failure with no runner/steps/logs is blocked/unknown—not pass and not proof of a test assertion failure.

This contract provides idempotent replay and conservative at-most-once dispatch for the same operation ID where every participating receiver enforces it. It does not promise exactly-once effects across unrelated databases or remote services. Crash recovery across such systems still requires receiver-enforced idempotency or a durable outbox plus reconciliation.

## 4. Security and evidence rules

- Hash integrity is not issuer authenticity. Signed evidence requires a provisioned trusted key ID and public-key trust anchor independent of the payload producer.
- Freshness, schema validity, authorization, execution observation and revision binding are separate checks; no one check substitutes for the others.
- Public evidence endpoints use HTTPS, reject redirects, enforce bounded response size and timeouts, and disable cache reuse for trust decisions.
- Local evidence may support development or diagnostics, but does not become procurement or production authority automatically.
- Private repository metadata belongs only in access-controlled inventories; public registries contain public metadata only.

## 5. Candidate implementation mapping (not yet end-to-end verified)

- [Great Scale PR #129](https://github.com/doitupsolutions810-crow/great-scale/pull/129): public inventory, proposed interface map and promotion-evidence checks.
- [Living Intermediate Control Plane PR #34](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/34): bounded HTTPS production-attestation fetch with exact-source binding, no-cache behavior and explicit unknown/hold behavior.
- [Capability Authority PR #12](https://github.com/doitupsolutions810-crow/capability-authority/pull/12): persistent operation state, stable intent/receipt event IDs, payload conflict rejection, durable receipt read-back and indeterminate recovery.
- [CycleKernel PR #13](https://github.com/doitupsolutions810-crow/CycleKernal/pull/13): stable chat-save key, canonical request digest, sparse unique MongoDB index, post-write reconciliation and ancillary-failure separation.

The components currently use service-specific storage and adapters. These PRs are candidate parts of the contract, not a deployed transaction spanning all four repositories.

## 6. Release success criteria

A cross-repository path may be marked `verified` only after all of the following pass against pinned candidate SHAs:

- identity/capability mismatch is denied before the effect;
- a duplicate identical operation returns the original durable result without a second effect;
- reusing an operation ID with a different request digest is rejected;
- failure before effect leaves a state known to be retry-safe;
- failure after a possible effect but before receipt persistence returns indeterminate and does not automatically re-execute;
- lost receipt acknowledgement is reconciled by the same operation ID;
- corrupted/missing receipt, invalid signature, stale source, wrong schema and stale revision fail closed;
- ancillary cache/metrics failure does not falsely report that the primary write failed;
- test output is linked to the exact source SHA, workflow run/job, observed steps and result;
- hosted CI executes the tests and a real dependency integration test verifies the actual MongoDB/SQLite/HTTP or relay boundaries.

No proposed edge should be upgraded to verified from documentation-only, isolated-harness or no-step workflow evidence.
