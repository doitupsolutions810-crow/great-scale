# Descent CLVIII — Missing Evidence Is Unknown, Not Failure or Success

## Finding

A Boolean CI predicate collapses several epistemically different states into `False`: a known failed run, a missing run, a stale run, a still-running job, or a green status from an unrelated provider. That is enough to reject authorization, but it is not enough to describe what is known.

The current branch's combined commit statuses included successful external statuses (CodeRabbit and Vercel), while the GitHub Actions workflow-run query for the branch head returned no qualifying pull-request run. That supports the conclusion "required CI execution evidence was not observed through this query," not "the code passed" and not necessarily "the code failed."

## Three-valued model

Let (E) be the evidence retrieved for candidate (c).

[
operatorname{Classify}(E,c) in {mathbf{PASS},mathbf{FAIL},mathbf{UNKNOWN}}
]

- **PASS:** a completed, successful GitHub Actions pull-request run matches the exact head SHA, base SHA, and required workflow.
- **FAIL:** a completed, qualifying run for that same candidate has the explicit `failure` conclusion. Cancellation, timeout, and action-required states remain UNKNOWN because they do not prove that tests failed.
- **UNKNOWN:** evidence is absent, stale, incomplete, from the wrong provider/event/workflow, or otherwise insufficient.

For authorization, both FAIL and UNKNOWN must block promotion, but they must not be reported as the same scientific observation:

[
operatorname{MayPromote}(E) Rightarrow
operatorname{Classify}(E,c)=mathbf{PASS}
]

[
mathbf{UNKNOWN}
emathbf{FAIL}, qquad
mathbf{UNKNOWN}
emathbf{PASS}
]

## Integration

`test_great_scale_clviii_three_valued_ci_evidence.py` checks absence, external status, exact success/failure, stale candidate, and incomplete-run cases. It is included in the aggregate `npm run all` command.

## Limits and next step

The local classifier tests the decision model; it does not itself query or authenticate GitHub. The workflow-run query may be scoped or paginated, so an empty result is evidence that no run was returned by that query, not a proof that no run exists anywhere. The production integration must fetch the required workflow run set, bind it to the current candidate, and preserve the distinction between a confirmed failure and unavailable evidence.

Full `npm run all`, clean-checkout build, and live branch protection remain unverified.
