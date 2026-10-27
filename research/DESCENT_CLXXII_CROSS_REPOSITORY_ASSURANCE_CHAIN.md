# Descent CLXXII — one assurance chain across the repositories

## Finding

Three repositories implement different pieces of one assurance problem:

- living-intermediate-control-plane decides whether procurement authority may be exercised from public evidence or an explicitly opted-in degraded fallback.
- capability-authority records control-plane events in a serialized ledger, with stable event identity and a JSON projection that still has a separate commit boundary.
- great-scale verifies whether required invariants have reachable tests, whether those tests actually ran, and whether the observed run applies to the reviewed revision.

These controls compose, but none substitutes for the others. Correct authorization cannot repair an incomplete event projection; a valid event hash chain cannot prove external freshness or projection completeness; and a test manifest cannot prove execution when the runner never starts.

## Shared acceptance contract

For candidate revision R and policy decision P, define:

- Policy(P): the authorization rule is satisfied, including explicit opt-in for a degraded local fallback.
- Complete(E): event and evidence state is complete to a verifiable sequence/checkpoint, not merely a valid prefix.
- Authentic(E): evidence provenance is authenticated to the trust boundary, such as source identity and an independently verifiable signature where required.
- Fresh(E,t): source-generated time/expiry or a monotonic checkpoint rules out stale evidence at decision time t.
- Reach(T,C): every required test T is reachable from the canonical test command C.
- Execute(T,R): the test body actually executes against the candidate revision R.
- Bound(R): the recorded run head equals the exact reviewed R.
- Pass(R): the required executed checks report success.

A system acceptance claim is justified only if:

\[
Accept(R,P,t) =
Policy(P)\land Complete(E)\land Authentic(E)\land Fresh(E,t)
\land Reach(T,C)\land Execute(T,R)\land Bound(R)\land Pass(R)
\]

The three-valued operational rule is fail-closed: any false or unknown predicate means acceptance has not been established. An absent runner, zero steps, stale receipt, missing projection event, or unknown provenance is not a pass.

## Evidence and open gates by repository

### living-intermediate-control-plane

Open PR #29: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/29

The PR branch removes FORCE_PROCUREMENT as an authorization bypass and requires core readiness plus either a verified public contract or an observed local fallback with explicit local opt-in. It also tightens HTTPS endpoint and schema checks. These are policy and contract-conformance improvements, not proof of fresh source evidence.

Remaining gates include source-generated freshness/expiry, signed or otherwise independently authenticated status provenance, an immutable receipt, and a sequence/checkpoint. The latest observed hosted run, 40425359386, failed before any steps ran (runner_id=0, zero steps). This does not establish a source-test failure or pass. The PR remains draft and unmerged.

### capability-authority

Open PR #12: https://github.com/doitupsolutions810-crow/capability-authority/pull/12

The branch integrates serialized SQLite ledger appends, stable event IDs and replay handling, fail-closed index loading, and atomic JSON projection replacement. A deeper source audit found that `EvidenceIndex` also uses a sidecar inter-process lock and rebuilds the JSON projection from the verified ledger inside ingest/query/stats paths. Under the same-filesystem assumption, with all projection writers honoring that lock, this mitigates the previously described stale-snapshot/lost-update race; the stale-writer claim should not be treated as an established remaining defect.

The separate commit boundary still exists: the SQLite append can commit before the JSON projection write completes. A projection-write error can therefore be returned after the authoritative event is durable. Because the ledger is authoritative and the JSON index is rebuildable, a subsequent query/stat refresh or retry using the same non-empty stable `event_id` can repair the projection. A new PR #12 regression simulates this exact post-commit projection failure and verifies query repair plus idempotent retry; it is committed but not yet executed in the full repository suite. Retries without a stable event ID are not guaranteed idempotent.

A valid hash-chain prefix still cannot prove that the ledger tail was not truncated. A monotonic sequence/watermark plus an independent checkpoint is still needed when adversarial or accidental tail truncation must be detected.

The current hosted run 40414560305 reports both test and slim-probe failing before steps ran (runner_id=0, zero steps); it supplies no test conclusion. The PR remains draft and unmerged.

### great-scale

Open PR #128: https://github.com/doitupsolutions810-crow/great-scale/pull/128

The branch now consolidates the canonical aggregate command and adds adversarial regressions for source-level test-reachability errors. A reconstructed local harness passed 10/10 expected-behavior cases, but this is not execution of the committed repository file or the full aggregate suite.

The latest observed hosted run 40425956377 on head 1f47defdaa4a100738d04ee1ca3c021e08eb191f failed before the job began (runner_id=0, zero steps). The AST audit can provide limited reachability evidence, not runtime execution proof. The PR remains draft and unmerged.

## Mitigation path

1. Resolve the account/repository Actions execution blocker through the GitHub settings and billing/authorization surfaces. The available repository connector cannot change those account-level settings.
2. Run the canonical test command from a clean checkout of each exact PR head on a trusted runner.
3. Record run URL, head SHA, job/step list, exit code and required-test coverage. A zero-step run is classified as unavailable evidence.
4. Close the source evidence gaps separately: source freshness/expiry and provenance for the control plane; transactional projection/reconciliation and an independent checkpoint for Capability Authority.
5. Re-evaluate all predicates after any new commit. A passing run on an older SHA cannot certify a newer candidate.

## Great Scale synthesis

The complete chain is:

\[
\text{Policy} \rightarrow \text{Evidence} \rightarrow \text{Durable State}
\rightarrow \text{Reachable Tests} \rightarrow \text{Observed Run}
\rightarrow \text{Revision-Bound Acceptance}
\]

Each arrow is an independently testable contract boundary. The profound result is that system correctness is not one boolean: it is a conjunction of authority, completeness, authenticity, freshness, execution, and revision identity. The system must keep its state as unknown until every required predicate has evidence.


## Follow-up verification update — 2026-10-27

The CI-evidence classifier in `test_great_scale_clxxiii_ci_execution_evidence.py` was executed from the fetched source in an isolated Python harness: **4/4 cases passed**, including the critical rule that a zero-runner/zero-step failure is UNKNOWN rather than FAIL or PASS. This is a local isolated run, not the full repository aggregate.

The latest Great Scale hosted run [40427882876](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40427882876) was retried (attempt 2) on head `3371e750d30b6d2d8907762926e78a5718588ec8`; it again ended with `runner_id=0` and zero steps. A retry therefore did not resolve runner availability. The source tree also contains an explicit regression for lambda-wrapped test references in a registry; the current auditor accepts only bare test-function names as registry entries.

A retry request for the Great Scale run succeeded, but retries for the other two repositories were blocked by the available action interface. The existing control-plane and Capability Authority run states therefore remain unchanged. No full suite or production deployment is claimed.


## Descent CLXXIV / Capability Authority recovery refinement

The new source-freshness contract in the control plane is orthogonal to ledger completeness. The Capability Authority projection is now assessed as a rebuildable materialized view with cross-process serialization—not as an unprotected pair of stale snapshots. Acceptance still requires the ledger identity/replay contract, recovery after projection-write failure, proof that the queried projection was reconciled to the verified ledger, and an independent checkpoint if tamper-evident completeness is required. The newest Capability Authority candidate after adding the recovery regression is `dd8c4e38136d3e3e81891045be0ace216a6c5253`; hosted run [40429217283](https://github.com/doitupsolutions810-crow/capability-authority/actions/runs/40429217283) exposed zero steps/logs, so the new test remains unexecuted by hosted CI.


## Descent CLXXV — signed source binding and unambiguous contract gates

The cross-repository status path now has a concrete producer candidate in [CONTROL12 Lattice Ops PR #31](https://github.com/doitupsolutions810-crow/control12-lattice-ops/pull/31) and matching source-authentication checks in [Control Plane PR #29](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/29).

The producer candidate exposes read-only GET routes for status and schema, requires an owner-configured Ed25519 keypair, issues source timestamps on each request, digest-binds canonical status JSON, signs the digest envelope, verifies its own timestamp/digest/signature/schema, and returns 503/no authority if signing configuration is missing. The consumer pins source identity/key ID/public key independently and validates status and schema separately. No production key was created, and the producer has not been deployed.

The semantic gate collision is resolved in the contract by giving the evidence-console's own checks identifiers E0–E6. Production readiness gates G0–G6 remain under the production evaluator. This prevents the status service from turning its own contract-health response into a production GO claim.

Local evidence for this descent:
- Node producer source harness: 8/8 cases passed with an ephemeral Ed25519 keypair.
- Great Scale signed-evidence acceptance model: 8/8 cases passed. The model treats signature verification as an external predicate and is not the cryptographic implementation.
- Earlier isolated freshness model: 6/6; isolated JavaScript freshness rule harness: 7/7.

The hosted repository suite still lacks observable execution because the connected GitHub Actions jobs report empty step lists and logs are unavailable. The live evidence hostname is not verified; the producer scaffold must still be deployed to the reviewed Vercel project with an owner-approved key and independently pinned consumer public key. Until those steps and a successful exact-head test run occur, procurement remains HOLD_EVIDENCE_CONTROL and production remains NO_GO.

Acceptance remains a conjunction:

\[
Accept(R,P,t) = Policy(P) \land Complete(E) \land Authentic(E) \land Fresh(E,t)
\land Reach(T,C) \land Execute(T,R) \land Bound(R) \land Pass(R)
\]

An absent runner is unknown execution evidence; freshness without a source signature is not authenticity; and a signed, fresh status object still does not prove complete ledger history without an independent checkpoint.
