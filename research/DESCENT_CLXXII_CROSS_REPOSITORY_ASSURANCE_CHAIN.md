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


## Descent CLXXVI — exact contract surface and nested gate integrity

### New source-level finding

The next review found a second-order schema gap: a validator can check that the expected field is described while still accepting a schema widened by an enum that contains both the expected and a weaker value. It can also miss unexpected fields inside an otherwise valid gate record if it only extracts id and status before checking the payload. Freshness plus a valid signature does not remove the need for exact structure checks.

The current v5.4.0 candidate closes this in both consumers and producer verification:

- Trust fields using enum are accepted only if the enum is the singleton expected value; const remains the canonical form.
- Status and schema root field sets and schema required keys must exactly match the contract. Unknown root fields, duplicate required keys, and missing fields fail closed.
- The schema root and array-form gate entries are closed with additionalProperties: false; their property/required sets are checked explicitly.
- Gate records may contain exactly id and status. The only accepted evidence-console field name is gates; the aliases results and gateStatuses cannot substitute for it.
- The producer's own verifier applies the same exact-field rules instead of merely generating a permissive schema and assuming the generator is correct.

The evidence-console's E0–E6 are checks on the console's signed contract surface. The separate production gate family G0–G6 is unchanged. A valid console contract may authorize only the procurement-trust step; it cannot turn production to GO.

### Candidate identity and regression inventory

Current draft heads observed during this pass:

- [CONTROL12 Lattice Ops PR #31](https://github.com/doitupsolutions810-crow/control12-lattice-ops/pull/31), head 7358374f173982caaf475fe11a297477e9dcc570: evidence-console producer routes, Ed25519 signing, strict procurement validator, and producer/procurement regressions. The committed test sources currently contain 12 producer tests and 24 procurement evaluator tests.
- [Living Intermediate Control Plane PR #29](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/29), head cf7088adddfdb14064e08abf6815e7853f8e675f: independent source signature verification, source freshness, exact schema fields, canonical gate identifiers, and nested gate-entry checks. The committed evidence-console test source currently contains 23 tests.
- [Great Scale PR #128](https://github.com/doitupsolutions810-crow/great-scale/pull/128), head 4c881dec3c186c750d0bc47b26aa566938518966: canonical assurance model and source-freshness test wiring.
- [Capability Authority PR #12](https://github.com/doitupsolutions810-crow/capability-authority/pull/12), head dd8c4e38136d3e3e81891045be0ace216a6c5253: rebuildable projection/recovery work remains unverified by full suite.

An independent local Node contract harness passed 16/16 bounded cases, including signed fresh acceptance, post-signature payload mutation, stale/expired/future status, wrong key, widened schema values, unknown fields, gate aliases, extra nested gate fields, and keeping production NO_GO separate. This is an isolated model harness—not execution of the committed repository tests or proof that all source files run together.

### Hosted execution and live status

The exact current candidate hosted runs still do not expose test execution:

- Lattice Ops run [40431822210](https://github.com/doitupsolutions810-crow/control12-lattice-ops/actions/runs/40431822210): startup_failure, no jobs exposed.
- Control Plane run [40431908618](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40431908618): both recorded jobs failed/skipped; step endpoint returned an empty list and log retrieval returned BlobNotFound.
- Great Scale run [40431757658](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40431757658): step endpoint empty, logs unavailable.
- Capability Authority run [40429217283](https://github.com/doitupsolutions810-crow/capability-authority/actions/runs/40429217283): prior zero-step run remains the latest observed for its candidate.

These are unknown execution evidence, not source-test failures and not passes. The public evidence-console endpoint could not be freshly retrieved through the available read path in this pass. The previously recorded 404 remains the last explicit HTTP observation; no current HTTP status is asserted here.

No production private key was generated, no Vercel deployment was performed, and no PR was merged. The producer must be deployed under the reviewed project with an owner-approved signing key; the consumer's key ID/public key must be installed independently; both live endpoint responses must then pass the exact contract check. Until those steps and exact-head CI execute successfully, procurement stays held and production remains NO_GO.

The acceptance formula remains conjunctive:

Accept(R,P,t) = Policy(P) AND Complete(E) AND Authentic(E) AND Fresh(E,t) AND Reach(T,C) AND Execute(T,R) AND Bound(R) AND Pass(R)

A signature authenticates the submitted status object; it does not independently prove complete ledger history. The separate sequence/watermark/checkpoint requirement remains open.


## Descent CLXXVII — close the JSON Schema vocabulary, not just the fields

The next hardening layer addresses a schema-language subtlety: a schema can retain all required keys and still introduce unreviewed constraints through other JSON Schema keywords. Checking familiar fields alone is not equivalent to checking the meaning of the whole schema.

The producer, Control Plane consumer, and procurement evaluator now require the exact schema shape generated by the contract:
- Schema root keys are exactly `$schema`, `type`, `additionalProperties`, `required`, and `properties`.
- The E0–E6 array schema keys are exactly `type`, `minItems`, `maxItems`, `uniqueItems`, `allOf`, and `items`.
- The item schema keys are exactly `type`, `additionalProperties`, `required`, and `properties`.
- Each `allOf` rule and each `contains` schema must have its exact key set, a single required `id`, and a single `const` for the corresponding contract-check ID.
- The item `id` schema is only an enum of the exact E0–E6 set; the item `status` schema is only `const: READY`.

This rejects unreviewed top-level or nested keywords such as `not`, `anyOf`, and `patternProperties`, as well as the previous classes of widened enums and extra root or gate-entry fields. The same constraints are implemented on the producer's self-check, the Control Plane's independent validator, and the procurement evaluator.

New committed test cases cover schema keyword injection at the root and nested gate/coverage-rule levels in the producer, consumer, and procurement tests. The current candidate test inventories are 13 producer tests, 25 procurement evaluator tests, and 24 Control Plane evidence-console tests. These are *test source counts*, not claims that hosted CI executed them.

The local 16/16 contract harness previously passed its bounded modeled cases; that harness is not the repository test suite and does not include the latest schema-keyword additions yet. Hosted Actions continues to fail before exposing any test steps, so the committed regression additions remain unverified by CI. Exact-head workflow execution, live public endpoint verification, owner-approved signing-key configuration/deployment, and independent ledger tail checkpointing remain separate gates.
