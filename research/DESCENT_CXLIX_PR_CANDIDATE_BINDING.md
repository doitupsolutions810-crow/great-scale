# Descent CXLIX — CI evidence belongs to a tested candidate, not just a head SHA

## Finding

A pull-request test result is not identified adequately by the source branch head SHA alone. Standard GitHub Actions pull_request runs normally test the synthetic merge candidate, which depends on both the PR head and target branch. A changed base can therefore produce a different candidate while the head SHA remains unchanged. A head-only test also does not establish integration with the current base.

## Formal contract

Let H be the PR head commit, B the target/base commit, M the exact tested merge candidate, W the workflow definition/version used, and S the observed run conclusion. Accept merge-readiness evidence only when:

AcceptPRCI(H,B,M,W,S) = CandidateMatches(M,H,B) AND WorkflowIdentified(W) AND (S = success) AND RequiredTestsReachable(W).

H and M are not interchangeable. Branch names are mutable references; evidence must bind to immutable SHAs.

## Counterexample

Keep H fixed but advance the base from B1 to B2. The candidate changes from M1 = merge(H,B1) to M2 = merge(H,B2). A successful run for M1 cannot certify M2, even though the PR head SHA is unchanged.

## Great Scale mapping

- State identity: record immutable H, B, and tested M, not just branch names.
- Transition integrity: verify the tested candidate derives from the recorded head/base pair.
- Verification reachability: confirm the canonical command ran under identified workflow W.
- Execution evidence: record run ID, tested SHA, conclusion, and job results.
- Freshness: any head/base/workflow change invalidates candidate-specific acceptance.

The proof object is not simply (H, green), but a revision-bound tuple (H, B, M, W, run ID, S).

## Integration and limits

A contract test is added in test_great_scale_cxlix_pr_candidate_binding.py and wired into npm run all. This is a model test: it does not query a live Actions run, prove GitHub's actual checkout SHA, or establish that hosted CI passed. A successful run on the exact current candidate and its head/base tuple remains required. No merge, build, deployment, or production verification is claimed.
