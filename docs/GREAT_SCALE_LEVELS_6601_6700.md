# Great Scale — Levels 6601–6700: two-SHA verification contract

**Status:** code and regression-fixture changes committed on the existing PR #89 research branch. The official test suite remains unverified because hosted Actions jobs fail before producing step records.

## New source-derived finding

A pull-request verification path has two related but distinct commit identities:

1. **PR source-head SHA**: the commit at the tip of the pull-request branch.
2. **Workflow checkout / merge-test SHA**: the commit actually checked out and tested by a `pull_request` workflow, typically the PR's synthetic merge commit against the current base branch.

They must not be collapsed into one field. GitHub's workflow-run metadata exposes the PR-associated head SHA; the canonical receipt records both `commit` (from `git rev-parse HEAD`) and `github_sha` (from the workflow environment). For a pull-request workflow that checks out the merge ref, the receipt's checkout SHA may differ from the PR source-head SHA.

The current PR #89 snapshot demonstrates distinct values for `head_sha` and `merge_commit_sha`. Recent workflow-run metadata reports `head_sha` matching the PR branch commit. This supports treating the source head and merge-test commit as separate identities.

A gate that requires `run.headSha = candidate.sha = receipt.commit` can therefore reject legitimate pull-request runs, or encourage an unsafe workaround that silently drops one identity. The contract must represent both values and bind each to the appropriate trusted platform field.

## Code integration

The existing `promotion_gate.js` now requires:

- the candidate SHA to equal the current PR source-head SHA;
- the authenticated workflow-run head SHA to equal that PR source-head SHA;
- the run event to be `pull_request` and the run attempt to be a positive integer;
- the current PR merge-test SHA to be a valid full SHA;
- receipt `commit` and `github_sha` to equal that merge-test SHA;
- receipt `github_run_attempt` to match the authenticated run attempt;
- the complete v1 producer receipt schema, including runtime fields, timestamp, repository, run ID and runner name.

The promotion result remains `ELIGIBLE_FOR_PROMOTION_REVIEW`, not automatic merge or deployment authorization. The collector must populate run event/attempt and the PR merge-test SHA from authenticated platform responses, not from caller assertions.

The `test_promotion_gate.js` fixture now models the PR head and merge-test SHA separately and adds adversarial cases for mismatched merge SHA, run event, run attempt, receipt SHA, timestamp and runtime metadata.

## Formal contract

Let (H) be the current PR source head, (M) the current merge-test commit, (R) the authenticated workflow-run metadata, and (E) the canonical receipt.

[
H = SHA_{candidate} = SHA_{PR-head} = SHA_{run-head}
]

[
M = SHA_{PR-merge-test} = SHA_{receipt.commit} = SHA_{receipt.github}
]

[
Attempt_R = Attempt_E
]

All three conditions are necessary. They establish identity binding across the source branch, the exact tested merge result, and the execution attempt. They do not by themselves prove that the collector is authentic or that the tests are adequate.

## Test and verification status

- Source updated and fetched back from the research branch.
- Regression fixture updated and fetched back; it now distinguishes PR source head from merge-test SHA.
- The suite contains 47 named gate tests after the new adversarial cases.
- **Official execution is not verified:** the latest observed GitHub Actions run failed with `steps: null`, `runner_id` absent and no executed-step summary. This is an infrastructure/execution-evidence failure, not proof that the assertions failed.
- No local command execution was available through the connected GitHub interface. Do not represent the 47 tests as passed until they actually run.

## Great Scale mapping

| Level | Mathematics | Engineering / science | Gate |
|---|---|---|---|
| 6601 | (H 
e M) may be valid; identity types matter | Distinguish source head from tested merge result | Separate fields |
| 6610 | (H=SHA_{candidate}=SHA_{PR}=SHA_{run}) | Bind platform run to the current PR head | Head-SHA equality |
| 6620 | (M=SHA_{merge}=SHA_{receipt}) | Bind receipt to the exact checkout/tested merge result | Merge-SHA equality |
| 6630 | (Attempt_R=Attempt_E) | Prevent retry/attempt ambiguity | Attempt equality |
| 6640 | Full producer output must satisfy the consumer's versioned type | Prevent receipt schema drift | Canonical receipt fixture |
| 6700 | (Trust = identity binding + authenticated evidence + valid inference + scope control) | Verification is compositional across source, merge result, execution and receipt | Official suites plus independently retrievable evidence |

## Candidate finding

**Reliable verification requires typed identity across layers, not one overloaded “commit SHA.”** A PR's source head, the workflow's tested merge result, and the workflow attempt are different identity dimensions. A trustworthy promotion gate must bind them explicitly and fail closed if any relationship is missing or contradictory.

This is a software assurance finding, not a physical law or empirical validation of a quantum-geometry model.
