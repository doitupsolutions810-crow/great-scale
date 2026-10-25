# Descent CXLVIII — Verification reachability is a precondition for evidence

## Finding

A test can exist, be correct, and be listed in a canonical command while still failing to provide evidence for a proposed revision if the workflow that should execute it is unreachable for that pull request.

The CI workflow on this branch previously declared:

```yaml
pull_request:
  branches: [main]
```

The stacked research PR targets `research/descent-civ-effect-evidence-boundary`, not `main`. Therefore this branch's own pull-request event does not match that branch filter. A configured `workflow_dispatch` trigger is not equivalent to an observed run: dispatch must actually occur, and the run must be tied to the reviewed head.

## Formal contract

Let:
- (T_R) be the required tests for revision (R);
- (C) be the canonical command graph (here, `npm run all`);
- (W) be the event/branch workflow trigger predicate;
- (H) be the commit SHA actually checked out by the run;
- (S) be the run conclusion.

Then CI evidence for (R) is acceptable only if:

[
operatorname{AcceptCI}(R) =
operatorname{Reachable}(T_R,C)
land W(	ext{event},	ext{base})
land (H=R)
land (S=	ext{success}).
]

This is a conjunction, not a score: a passing isolated test cannot compensate for a missing trigger, and a successful run on an older SHA cannot certify the current head.

## Integration

- Removed the target-branch restriction from the `pull_request` trigger in `.github/workflows/ci.yml`; PRs to stacked research branches can now match the trigger once that workflow definition is active on the base branch.
- Added `test_great_scale_cxlviii_verification_reachability.py` to characterize the workflow/aggregate-command contract.
- Kept `npm run all` as the canonical entry point and retained the prior CXLV and CXLVII tests.

Important GitHub Actions nuance: a workflow-file edit inside a pull request does not itself prove that the edited workflow ran for that same pull request. The base-branch workflow definition and actual event run still matter. The change may require merge into the relevant base branch or a real manual dispatch before it can be exercised.

## Great Scale mapping

- **Identity:** bind each result to an immutable commit SHA (R).
- **Reachability:** every required test is reachable from canonical CI command (C).
- **Trigger:** the event/base predicate actually selects the workflow.
- **Execution:** observed checkout SHA equals (R).
- **Conclusion:** the run reports success, with inspectable job evidence.

Thus:
[
	ext{Verification} 
eq 	ext{TestExists}
]
and
[
	ext{Verification}(R) = 	ext{Reachable} land 	ext{Triggered} land 	ext{RunHead}=R land 	ext{Success}.
]

## Verification status and limits

The workflow edit and regression test are committed proposals, not proof of a hosted run. No claim is made here that `npm run all` passed, that GitHub Actions ran on the updated head, or that a build/deployment was verified. A fresh hosted run on the exact final SHA remains the decisive next check.
