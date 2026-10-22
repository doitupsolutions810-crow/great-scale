# Great Scale Levels 5101–5200 — Evidence must remain bound to the object being promoted

## Descent target

Levels 5001–5100 formalized promotion as a conjunction over repository, commit, run, job, receipt, and artifact. The next question is temporal: can evidence that is valid for a commit still authorize a decision after the pull request changes?

No. A run can truthfully report success for commit C while the current pull-request head is C′. Even if the original evidence graph is internally consistent, it no longer describes the object currently proposed for promotion.

## Integrated guard

The evidence envelope accepted by `promotion_gate.js` now requires a pull-request snapshot:

```js
pullRequest: {
  number: 89,
  state: "open",
  headRepository: "owner/repository",
  headSha: "<full 40-character commit SHA>"
}
```

The gate fails closed unless the PR number is valid, the PR is still open, the head repository equals the candidate repository, and the PR head SHA equals the candidate SHA. Its exact schema rejects missing or extra fields, as with the other evidence records. Four additional adversarial cases were added to `test_promotion_gate.js`: changed head SHA, mismatched head repository, closed PR, and invalid PR number.

This is a snapshot-binding control, not a cryptographic authenticator. The evidence collector must obtain the PR snapshot from an authenticated platform API. A fabricated JSON snapshot can still pass structural validation if the collector boundary is not trusted.

## Mathematical statement

Let P be the repository, C the candidate commit, R the workflow run, J the job, Q the verification receipt, A the artifact, and H(t) the platform-observed pull-request state at time t. Let E(P,C,R,J,Q,A) express the original evidence conjunction. Define

[
H_C(t) := operatorname{Open}(H,t)
land operatorname{Repo}(H,t)=P
land operatorname{HeadSHA}(H,t)=C.
]

The strengthened review predicate is

[
operatorname{ReviewEligible}(P,C,t)
= E(P,C,R,J,Q,A) land H_C(t).
]

If the PR head advances from C to C′, where C′ differs from C, then the evidence for C does not establish review eligibility for C′:

[
C' 
e C land operatorname{HeadSHA}(H,t_1)=C'
Longrightarrow 
eg H_C(t_1).
]

The important temporal limit is

[
operatorname{ReviewEligible}(t_0)

otRightarrow
operatorname{ReviewEligible}(t_1).
]

A successful check at time t₀ is not a timeless fact about a mutable branch.

## Residual TOCTOU obligation

The gate returns `ELIGIBLE_FOR_PROMOTION_REVIEW`; it does not merge. The pull request can change after the snapshot is collected. Therefore downstream merge/promotion logic must re-fetch the PR head immediately before acting and use a compare-and-swap style precondition requiring the expected full head SHA C. If the observed head is different, it must stop and require fresh CI evidence. A prior gate result must never be treated as a reusable bearer token for a moving branch.

This separates three properties:

1. **Integrity:** the run, receipt, artifact, and candidate all name the same immutable commit.
2. **Freshness:** the currently open PR still points at that commit when the decision snapshot is collected.
3. **Atomicity at action time:** the merge operation itself refuses to act if the PR head has changed since the check.

The patch adds the second property structurally and specifies the third as an outstanding downstream obligation. It does not claim that the current gate alone solves atomicity.

## Test and execution status

The new adversarial cases are integrated into the repository's test source. However, they have not yet been executed by the committed `npm test` command in this environment, and `python3 test_descent.py` has also not been run on this head. Code integration is not the same as an executed regression suite.

The latest preceding hosted run had no usable logs or artifact and no executed step list. This new commit requires its own runner execution and evidence. Keep PR #89 draft and unmerged pending a real runner, both suites passing on the exact head, platform-observed logs/artifact, and human review.

## Great Scale mapping

| Level | Mathematics | Science | Status |
|---|---|---|---|
| 5101 | Candidate and current PR head share one exact identity: `headSHA = candidateSHA`. | A passing historical run does not test a later commit. | Gate source changed; committed tests added, not yet run. |
| 5102 | Eligibility gains `Open(PR) ∧ Repo(PR)=P ∧ HeadSHA(PR)=C`. | Open/closed state and branch identity are platform observations, not mathematical axioms. | Integrated on research branch; requires trusted API collector. |
| 5103 | Validity is time-indexed: (E(t_0)\not\Rightarrow E(t_1)). | Mutable refs create a TOCTOU hazard even though commit objects are immutable. | Derived; four adversarial regression cases added. |
| 5104 | Safe action needs an expected-head precondition, analogous to compare-and-swap. | Downstream merge must reject a changed SHA instead of reusing stale eligibility. | Design obligation documented; atomic merge precondition is not implemented by this gate. |
| 5105–5200 | Continue with collector authentication, freshness, immutable decision records, and ref-movement race tests. | No physical quantum-geometry result follows from this software-assurance model. | Research frontier; hosted runner blocker remains. |

## Profound finding

**Evidence validity is indexed not only by identity, but by time and action.** Immutable commit hashes prevent one form of ambiguity; they do not freeze the mutable branch pointer or make a check-and-then-act sequence atomic. A robust promotion protocol needs (i) provenance-bound evidence for commit C, (ii) a fresh observation that the proposed object is still C, and (iii) an action-time precondition that refuses to act if that identity changed.

This extends the evidence-graph principle from a static conjunction to a temporal safety condition. It is a software-assurance finding, not a new physical law.
