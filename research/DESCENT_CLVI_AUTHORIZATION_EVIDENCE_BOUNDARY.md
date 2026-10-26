# Descent CLVI — Authorization Evidence Is Not Its Own Authentication

## Finding

The CLIV model accepts a Boolean named `server_enforced_authorization`. That Boolean is a useful abstract assumption, but the model cannot establish that it came from GitHub or that branch protection actually enforced the merge. A caller can supply `True`.

This is a trust-boundary gap in the model, not proof that GitHub's server enforcement is broken. It means the local predicate must not be cited as evidence that the remote server configuration is active.

## Formal distinction

Let (E) be an authorization-shaped record and (V(E)) be an independent verification step that authenticates its source and binds it to the merge candidate.

[
operatorname{WellFormed}(E) 
otRightarrow operatorname{Authentic}(E)
]

[
operatorname{Accept}(E) Rightarrow
operatorname{WellFormed}(E) land V(E) land
operatorname{Candidate}(E)=operatorname{Candidate}_{merge}
]

The CLVI regression checks evidence shape: issuer label, authenticated flag, candidate SHA, required-check result, and merge-policy-enforcement flag. These fields remain caller-supplied in the isolated model. Consequently, passing CLVI tests proves only that the predicate enforces its schema; it does not prove the authenticity of the record.

## Great Scale mapping

- **Claim:** the merge is authorized.
- **Observation:** provider reports the relevant check and merge-policy state.
- **Authentication:** independently validate provider provenance and response context.
- **Binding:** ensure the evidence identifies the exact candidate and current base.
- **Enforcement:** GitHub server-side branch rules/required checks/merge queue reject unapproved merges.
- **Audit:** record tested head/base, workflow revision, check-run IDs and conclusions, and final merge result.

## Integrated regression

`test_great_scale_clvi_authorization_evidence_boundary.py` rejects missing provenance fields, rejects candidate mismatch, and checks that required checks and server-policy enforcement are represented. It deliberately documents its own limit: a Python object cannot authenticate itself. A follow-up integration must read live GitHub checks and ruleset/branch-protection state through an authorized API and fail closed if those observations are unavailable.

## Verification status

This is a contract-level regression. The full aggregate suite, hosted CI, and live branch-protection/ruleset enforcement remain unverified. Do not infer that the server configuration is active from these local tests.
