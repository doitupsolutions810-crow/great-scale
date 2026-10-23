# Great Scale — Levels 8309–8316: Execution-Bound Evidence

## Deep finding

A verification receipt is a claim about an execution, not proof that the execution happened. A receipt can contain a plausible commit SHA, run ID, suite status, and artifact digest while being self-authored or copied from another run. Integrity of the JSON bytes does not establish issuer identity, workflow execution, or correspondence to the reviewed commit.

The verification relation needs independently sourced run evidence:

V = C AND R AND A AND S AND H AND Trusted

- C: receipt commit equals the workflow's independently retrieved head SHA.
- R: run ID and attempt match.
- A: the workflow completed with successful conclusion.
- S: every required suite has independently evidenced success.
- H: the digest of the retrieved artifact equals the receipt's expected digest.

Missing inputs produce UNRESOLVED; untrusted provenance produces UNTRUSTED; a contradiction produces MISMATCH; only all matched, trusted predicates produce VERIFIED.

## Great Scale map

| Level | Mathematics | Science / engineering meaning | Test gate |
|---|---|---|---|
| 8309 | Receipt is not execution proof | A self-report cannot authenticate itself | Reject missing run evidence |
| 8310 | receipt SHA = workflow head SHA | Evidence must bind to reviewed commit | Commit-mismatch counterexample |
| 8311 | (run ID, attempt) match | Retries are distinct executions | Attempt-mismatch regression |
| 8312 | status=completed AND conclusion=success | Queued, cancelled, and failed runs are not passes | Non-success run cases |
| 8313 | all required suites = passed | Aggregate status cannot substitute for suite evidence | Missing/failed suite cases |
| 8314 | SHA256(artifact) = receipt digest | Detect artifact substitution | Digest mismatch |
| 8315 | trusted source is a precondition | User-supplied metadata is not trusted GitHub evidence | Untrusted-source rejection |
| 8316 | VERIFIED = C AND R AND A AND S AND H AND Trusted | Promotion requires evidence binding, not just a receipt file | Positive/adversarial matrix |

## Implementation boundary

`execution_evidence.js` is a pure decision function. Its caller must obtain `runEvidence` independently (for example, from an authenticated GitHub Actions API adapter) and only set `trustedRunEvidence=true` after validating that source. Suite results must come from trusted step/job evidence or a suitable attestation; a workflow conclusion alone does not prove that a particular test command ran. The artifact digest must be calculated over actual downloaded artifact bytes.

This helper does not authenticate GitHub, fetch workflow metadata, verify signatures, or prove that the test suite is scientifically adequate. VERIFIED means the supplied evidence satisfied this contract under the caller's trust assertion—not that the mathematical model is physically true.

## Verification status

The focused regression file is `test_execution_evidence.js`. It should be run from the repository checkout and added to the canonical `npm test` command before promotion. Do not merge this draft based solely on authored tests or static source inspection.
