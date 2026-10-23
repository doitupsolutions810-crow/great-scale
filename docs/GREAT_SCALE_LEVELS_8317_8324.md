# Great Scale — Levels 8317–8324: Policy-Bound Evidence

## Deep finding

Execution-bound evidence is still incomplete if the test policy is implicit or can drift without changing the receipt. A green result is meaningful only relative to a declared verification contract. If the required suite list, workflow path, or receipt schema changes, old evidence must not silently be interpreted under the new contract.

This rung binds the receipt to the exact bytes of `verification-policy.json` using SHA-256. The canonical verification script writes that digest into the receipt; the decision function recomputes the digest from the checked-out policy and requires both the receipt and independently sourced run evidence to name it.

Let:

- (C): receipt commit equals independently sourced run head SHA.
- (R): run ID and attempt match.
- (A): workflow completed successfully.
- (S): all required suites are independently evidenced as passed.
- (H): actual artifact bytes hash to the receipt's expected digest.
- (P): receipt and run evidence bind to the checked-out verification-policy digest.
- (T): the run evidence was obtained from an authenticated, trusted source.

Then:

[
V = C \land R \land A \land S \land H \land P \land T
]

A missing input is `UNRESOLVED`; untrusted provenance is `UNTRUSTED`; contradictory evidence is `MISMATCH`; `VERIFIED` is returned only if every predicate holds.

## Great Scale map

| Level | Mathematical structure | Engineering interpretation | Adversarial test |
|---|---|---|---|
| 8317 | Evidence is relative to a policy (P) | “Passed” has no meaning without a named contract | Missing policy identity |
| 8318 | (P=) canonical policy bytes | Suite list, workflow path, and receipt schema are explicit | Unknown/malformed policy |
| 8319 | (h_P=mathrm{SHA256}(P)) | Policy identity is content-addressed | Policy digest mismatch |
| 8320 | (workflow=workflow_P) | Evidence must refer to the expected workflow file | Wrong workflow path |
| 8321 | (repository=repository_P) | A passing run from a different repository cannot be substituted | Repository mismatch |
| 8322 | (orall s\in S_P, result(s)=passed) | Missing or skipped required suite blocks verification | Missing/failed suite |
| 8323 | (V\Rightarrow T\land H\land P) | Hashes and policy identity do not authenticate their source | Untrusted-source rejection |
| 8324 | (V=C\land R\land A\land S\land H\land P\land T) | Promotion evidence is scoped, versioned, and fail-closed | Positive and mismatch matrix |

## Critical boundary

The policy digest proves which policy bytes are named; it does not prove that the policy is scientifically adequate, that the GitHub collector is authenticated, or that a particular test actually ran. The caller must retrieve workflow/run/job/step evidence independently. The artifact digest must be calculated over actual downloaded bytes by a trusted collector.

There is a further design constraint: a receipt cannot safely contain the digest of the very archive that contains that receipt, because changing the digest changes the archive bytes. To avoid this self-reference, the digest target must be a separate evidence bundle, or a precisely specified canonical payload that excludes the digest field. The current receipt artifact does not yet implement that separate bundle; therefore artifact-byte verification remains an integration obligation, not a passed test.

## Verification status

The new focused regression matrix covers policy mismatch, workflow/repository mismatch, malformed digests, missing suite evidence, attempt mismatch, and untrusted sources. The current test command includes `test_execution_evidence.js`. Do not interpret isolated tests as proof that the full repository suite or hosted CI passed. The current PR is stacked on a non-main base, while the observed main-branch workflow configuration only triggers pull requests targeting `main`; the absence of a run for the stacked PR is therefore consistent with a trigger-scope gap, not evidence of a test failure.
