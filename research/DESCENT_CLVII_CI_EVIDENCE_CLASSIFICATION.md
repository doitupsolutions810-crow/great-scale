# Descent CLVII — A green status is not a verified build

## Live observation

For Great Scale PR #128, the latest inspected candidate was `7824fadb98bc6bee80b5fe28cd2beb086e688a24`, based on `101a9b9aa8ff7f71ba6d2ca123190847873a4f2f`. GitHub's Actions-runs endpoint returned zero workflow runs for that head. The commit check-runs endpoint showed a successful Vercel Preview Comments check, not a successful test workflow. The repository rulesets endpoint returned an empty list; that does not by itself prove that no branch-protection rule exists, because branch protection is a separate API surface.

Therefore the observed green status cannot substantiate that `npm run all` executed successfully. This is a finding about the available evidence, not proof that the tests failed or that CI was intentionally bypassed.

## Formal contract

Let (E) be a status/run record and (S=(H,B,W)) the intended candidate head, base, and workflow.

```text
QualifyingCI(E,S) =
    provider(E) = GitHub Actions
    AND run_id(E) is nonempty
    AND head(E) = H
    AND base(E) = B
    AND workflow(E) = expected workflow
    AND event(E) = pull_request
    AND status(E) = completed
    AND conclusion(E) = success
```

A successful third-party status does not satisfy this predicate merely because its conclusion is `success`.

## Integrated regression

Added `test_great_scale_clvii_ci_evidence_classification.py` and wired it into `npm run all`. Four tests check: third-party green status rejected; exact completed Actions PR run accepted; missing run ID or stale head/base rejected; failed or wrong-event run rejected.

This remains a model of the evidence contract. It does not itself query GitHub or authenticate a run. Live API retrieval and merge-policy enforcement remain separate obligations.

## Run

```sh
python3 test_great_scale_clvii_ci_evidence_classification.py
npm run all
```

Do not declare merge readiness until the exact PR candidate has a qualifying hosted run and the relevant server-side merge policy is independently verified.
