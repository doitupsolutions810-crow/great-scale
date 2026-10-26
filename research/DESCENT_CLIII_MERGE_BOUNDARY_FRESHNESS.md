# Descent CLIII — Freshness must survive the merge boundary

## Finding

CLII binds successful CI evidence to a particular review snapshot. That still leaves a time-of-check/time-of-use (TOCTOU) gap: the snapshot may change after the freshness check and before the merge consumes the result. A green run for state S at time t does not establish that the state at merge time t+Δ is still S.

## Formal contract

Let the review state be:

\[
S_t=(H_t,B_t,W_t,M_t)
\]

where H is the PR head, B the target/base revision, W the workflow identity/revision, and M the tested merge candidate. Let E be successful run evidence bound to snapshot S_v.

The check-time condition is:

\[
\operatorname{Verified}(S_v,E)=
(E.runId\ne\varnothing)\land(E.conclusion=success)\land(E.state=S_v)
\]

But merge safety additionally requires:

\[
\operatorname{SafeMerge}=
\operatorname{Verified}(S_v,E)\land(S_{merge}=S_v)
\]

If the base advances, the head changes, the workflow changes, or the candidate is regenerated, then S_merge ≠ S_v and the old evidence must not authorize the operation. The alternative is an explicit provider-enforced merge-boundary mechanism that reruns or revalidates required checks for the exact candidate being merged.

## Regression model

Added `test_great_scale_cliii_merge_boundary_freshness.py`. It models:
- unchanged verified state accepted;
- base/candidate movement after verification rejected;
- head or workflow movement rejected;
- absent run ID and failed conclusion rejected.

This is an abstract TOCTOU contract test. It does not query GitHub branch protection, merge queues, required-check configuration, or actual merge events.

## Great Scale mapping

- **State:** immutable tuple (head, base, workflow, candidate).
- **Observation:** CI run is bound to a snapshot.
- **Transition:** repository state can change after observation.
- **Invariant:** evidence authorizes merge only if its snapshot still equals the merge candidate snapshot, or the provider revalidates at the boundary.
- **Operational control:** strict/up-to-date required checks or a merge queue that validates the exact candidate; record the actual merge SHA and run IDs.

## Verification status

The committed test was added to the research branch. A clean checkout, direct execution of the committed test, aggregate `npm run all`, and hosted CI have not yet been run for the new commit. This note does not claim the repository is merge-safe today; actual GitHub protection settings and a successful hosted run on the exact candidate must be inspected.
