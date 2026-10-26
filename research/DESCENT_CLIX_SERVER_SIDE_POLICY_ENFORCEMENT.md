# Descent CLIX — Repository Tests Cannot Enforce Repository Policy

## Observed configuration

On 2026-10-26, GitHub's public branch metadata for `great-scale` reported both `main` and `research/descent-cxli-evidence-projection-reconciliation` as `protected: false`, with branch-protection `enabled: false` and required-status-check enforcement `off`. The branch head at observation time was `6bd16f3451f7b425b9b2e0996d7027ab67a42bd3`. The Actions workflow-runs endpoint queried for that SHA returned zero runs. The branch metadata is public API evidence; the dedicated branch-protection endpoint itself returned 403 to the connected integration, so do not infer details beyond the exposed branch object.

## Finding

Local tests can assert that a policy *should* be enforced, but they cannot make GitHub enforce that policy. A test passing inside a PR does not by itself prevent that PR from merging. Enforcement is a property of the remote repository configuration and merge path.

This is the difference between a program invariant and an operational invariant.

## Formal gate

Let (T) mean qualifying CI passed for the exact candidate, (P) mean server-side policy is verified enforced, and (C) mean the evidence is bound to the candidate.

[
operatorname{MayMerge}=Tland Pland C
]

[
Pin{	ext{ENFORCED},	ext{NOT_ENFORCED},	ext{UNKNOWN}}
]

Both NOT_ENFORCED and UNKNOWN block promotion. A green status cannot compensate for missing policy enforcement:

[
Tland(P
e	ext{ENFORCED})Rightarrow
egoperatorname{MayMerge}
]

## Integrated regression

`test_great_scale_clix_server_policy_gate.py` tests that unknown or explicitly disabled policy blocks promotion even when CI passes, and that verified enforcement still requires both passing CI and candidate binding. It is included in `npm run all`.

## Operational remediation

Configure a ruleset or branch protection for `main` that requires the intended GitHub Actions check, blocks direct/bypass merges as appropriate, and requires up-to-date branches or a merge queue if that is the intended atomicity model. Then query the configuration and verify a real PR is blocked when the required check is absent. Repeat this for every branch that is a protected integration target. Do not mark the policy as verified based only on the local regression.

## Verification limits

The regression is a local decision-model test. It does not change repository settings, prove GitHub enforcement, or establish a hosted run. Full `npm run all` and clean-checkout build remain unverified.
