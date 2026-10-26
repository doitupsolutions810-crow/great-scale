# Great Scale — Levels 8349–8360: Receipt-to-Runner Identity Binding

## Research question

Can the promotion gate accept a structurally valid verification receipt whose declared runner name contradicts the runner identity returned by the authenticated platform job record?

## Finding

Before this increment, the gate required both `job.runnerName` and `receipt.runner_name` to be nonempty, but did not require equality. Thus, a valid-looking receipt could name a different runner than the platform job it was supposed to document. This is an evidence-consistency gap; it is not evidence that an attacker exploited the gate or that the receipt collector is authenticated.

## Integrated change

- Added a fail-closed equality check between the receipt's `runner_name` and the observed platform job's `runnerName`.
- Added a regression case that changes only the receipt runner name and requires the candidate to be blocked.
- Preserved the gate's limited meaning: eligible means eligible for human promotion review, not authorized to merge or deploy.

## Great Scale table

| Level | Mathematics | Science / engineering | Status |
|---|---|---|---|
| 8349 | Require (r_{receipt}=r_{platform}). | The receipt and platform job must identify the same runner. | Guard integrated. |
| 8350 | If (r_{receipt}\ne r_{platform}), then (E=0). | Contradictory provenance blocks eligibility. | Regression added. |
| 8351–8354 | Keep identity equality independent from suite outcome and SHA binding. | One matching field cannot substitute for the remaining proof obligations. | Source review only. |
| 8355–8358 | Separate structural consistency from collector authenticity. | Equal names do not cryptographically authenticate the source. | Trust boundary documented. |
| 8359–8360 | Promotion eligibility is a conjunction, not a score. | Any missing or inconsistent required edge blocks the conclusion. | Full suite and CI still unverified. |

Here (r_{receipt}) is the runner name recorded by the verification script, (r_{platform}) is the runner name returned in the platform job record, and (E\in\{0,1\}) denotes whether the gate is eligible for review.

## Verification boundary

This change and its regression were written to the research branch through the GitHub contents API. The repository's Node.js tests, Python descent suite, and build were not executed in this environment. No test pass is claimed. The prior CI blocker remains open: a run with runner ID 0, no runner name, no steps, and no logs cannot establish that tests executed.

## Profound finding

Evidence can be internally well-formed and still be relationally false. Great Scale should treat every provenance relation as an explicit invariant and preserve the distinction between:
1. schema validity,
2. cross-record consistency,
3. authenticated origin,
4. observed execution,
5. human authorization.
