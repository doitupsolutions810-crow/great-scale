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

The PR integrates serialized SQLite ledger appends, stable event IDs and replay handling, fail-closed index loading, and safer projection updates. The JSON projection remains a separate store/commit boundary. Stale writers can still omit events, and a valid hash-chain prefix does not by itself prove that the tail is complete. A same-transaction SQLite projection or rebuildable outbox with a sequence watermark is the stronger path; an independent checkpoint is still needed to detect tail truncation.

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
