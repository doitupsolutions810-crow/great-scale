# Descent CLXXIV — source freshness is not probe freshness

## Finding

The control-plane evidence probe checks the response's policy fields, seven gate identities, schema constraints, HTTPS transport, redirect behavior, and no-cache request directives. However, the v5.3.1 status contract has no source-issued generation time or expiry. The probe's `checkedAt` is created by the client. It proves when a request was made, not when the evidence was generated.

This creates a temporal trust-boundary gap:

[
	ext{FetchedNow}(E,t) \not\Rightarrow \text{GeneratedRecently}(E,t)
]

A stale but structurally valid `READY` document can be fetched now. No-cache directives do not repair absent source timestamps, and client-local time cannot be used as a substitute.

## Source-level mitigation integrated

The control-plane PR #29 now advances its evidence contract to v5.4.0 and requires, in both the status payload and its JSON schema:

- `sourceGeneratedAt`: source-generated ISO date-time, at most five minutes old at decision time, with up to 30 seconds of clock skew into the future.
- `sourceExpiresAt`: source-generated ISO date-time strictly later than the decision time and generation time, with total validity no longer than five minutes.

The validator fails closed on absent or unparsable timestamps, stale issuance, excessive future skew, expiry, invalid lifetime, or a schema that omits or weakens either timestamp field. The existing `checkedAt` remains diagnostic only.

The corresponding Node regression fixtures were upgraded to v5.4.0 and include tests for stale, expired, future-dated, missing, and schema-weakened freshness fields. These tests are included in the control-plane's existing `npm test` target.

## Executable model integrated in Great Scale

Added `test_great_scale_clxxiv_source_freshness.py` and wired it into the canonical `npm run all` command.

The six model cases cover:
1. fresh source issuance;
2. stale evidence fetched at a new client time;
3. expired source evidence;
4. generation time beyond allowed clock skew;
5. missing and timezone-free timestamps;
6. an overlong validity window.

The model makes the acceptance predicate explicit:

[
Fresh(E,t) = Parse(g) \land Parse(x) \land (g \leq t + \delta)
\land (t-g \leq \tau) \land (x > t) \land (0 < x-g \leq \tau)
]

where (g) is source generation time, (x) expiry, (delta=30s), and (	au=5min). In the assurance chain, `Fresh` is necessary but not sufficient.

## Important migration gate

The contract document in the control-plane branch still describes the deployed/public contract as v5.3.1 before this change; the v5.4.0 producer must be deployed before the public path can pass this stricter validation. I did not locate the status/schema producer in the CycleKernal main tree. Therefore, public-authority availability after this contract bump is **not verified**. This is intentional fail-closed behavior, not proof that the producer has been updated.

## What this does not prove

Timestamps alone do not authenticate the source: a malicious or compromised producer can forge its own time. They also do not prove that every event is represented. Signed provenance, monotonic sequence/watermark, reconciliation, and an independent checkpoint remain separate controls. The Capability Authority JSON projection remains a separate commit boundary and still needs transactional projection or a rebuildable outbox with sequence watermark.

## Verification boundary

The source-freshness model is a separate executable model, not an import of the live Node validator. The committed Node tests were added but could not be executed in a clean repository checkout here. Hosted Actions execution remains unavailable: the latest observed Great Scale run 40427995401 has a failed job but no exposed steps, and earlier attempts showed `runner_id=0` with zero steps. Do not classify this as a source-test pass or fail.

The next acceptance predicate remains:

[
Accept(R,P,t) = Policy(P) \land Complete(E) \land Authentic(E)
\land Fresh(E,t) \land Reach(T,C) \land Execute(T,R)
\land Bound(R) \land Pass(R)
]

Unknown in any required term remains rejection of the acceptance claim.
