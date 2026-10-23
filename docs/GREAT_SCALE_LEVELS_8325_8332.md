# Great Scale — Levels 8325–8332: Evidence Is Not Authority

## Profound finding

An evidence system can correctly establish that a specific artifact was tested under a named policy and still fail to establish that anyone had the right to deploy it. Verification and authorization are logically independent gates.

[
\text{Permit} = V \land I \land B \land Q \land W \land N
]

where:

- (V): execution evidence verifies against the exact tested commit and policy.
- (I): principal identity is independently authenticated.
- (B): approval is bound to the exact proposal ID, diff digest, and declared scope.
- (Q): required approval quorum and role policy are satisfied.
- (W): approval is within its validity window and maximum age.
- (N): nonce is unused and consumed atomically by a durable replay store.

A trust score, model confidence, random simulation value, or self-asserted `authenticated: true` field is not an identity credential and must not grant permission.

## Great Scale map

| Level | Mathematics | System meaning | Test gate |
|---|---|---|---|
| 8325 | (V \not\Rightarrow Permit) | Successful verification is not authorization | Valid test evidence with no approval still blocks |
| 8326 | (I=authenticated(principal)) | Authority must come from a trusted identity source | Unauthenticated principal blocks |
| 8327 | (B=(proposalId,diffHash,scope)) | Approval cannot be reused for a different change | Proposal/diff/scope mismatch blocks |
| 8328 | (Q: approvals \ge q) | Quorum is explicit policy, not a trust score | Insufficient quorum blocks |
| 8329 | (W: issued \le now < expires) | Approval has bounded validity | Expired/future-dated approvals block |
| 8330 | (N: nonceUnused) | Replay resistance is required | Reused or unknown nonce blocks |
| 8331 | (Permit=V\land I\land B\land Q\land W\land N) | Verification and authorization compose as separate gates | Adversarial policy matrix |
| 8332 | state transition requires explicit permit | No confidence score can silently authorize deployment | Score-only approval path prohibited |

## Cross-repository interpretation

- **TrainLLM:** the inspected proposal approval path accepts a proposal when a randomly generated counterfactual trust score exceeds 0.8, even without a real human approval. This must be replaced with authenticated, proposal-bound approval before production use.
- **CycleKernal:** promotion/demotion is a state transition. The state-aware demotion fix in PR #4 should remain separate from release authorization; a mathematically valid demotion decision does not grant permission to mutate a protected production environment.
- **Great Scale:** the new `authorization_gate.js` is a structural fail-closed gate and returns `ELIGIBLE_FOR_AUTHORIZED_EXECUTION_REVIEW`, not an execution command. It rejects mismatched proposal identity, diff digest, scope, role, quorum, time window, nonce, and untrusted identity evidence.

## Security boundary

This module does not authenticate a principal, verify signatures, or atomically consume a nonce. The production caller must obtain identity and approval evidence from an authenticated provider and consume the nonce transactionally before acting. The gate's boolean trust fields are structural assertions, not cryptographic proof. No production authorization claim is made.

## Verification status

The focused authorization test matrix contains 18 adversarial and positive cases and is wired into `npm test`. The new policy/evidence tests were run in an isolated local harness; the authorization-gate tests are authored but have not yet been run in the actual repository checkout. Full repository tests, hosted CI, build, and deployment remain unverified.
