# Descent CLIII — A Predicate Cannot Authenticate Its Own Inputs

## Finding

The CLII predicate establishes snapshot consistency only. Every field in its `Snapshot` dataclass is supplied by the caller. Therefore, an internally consistent fabricated snapshot can satisfy `accept_current`; the predicate has no independent observation channel with which to distinguish fabricated fields from GitHub-derived fields.

This is not a defect in equality logic. It is a trust-boundary limitation.

## Formal distinction

Let `P(S,E)` be the CLII consistency predicate, and let `A(E)` mean that evidence E was independently obtained and authenticated from the authoritative provider.

`P(S,E) = true` does not imply `A(E) = true`.

The safe acceptance rule is:

`Accept(S,E) = P(S,E) AND A(E) AND CandidateValid(E)`

where `A` must be established outside the data model—for example, by a trusted GitHub API adapter that retrieves the PR, workflow run, run jobs, workflow definition at the relevant revision, and tested commit metadata. `CandidateValid` must apply the provider's actual merge-candidate semantics, not a guessed parent convention.

## Practical consequence

The evidence adapter should produce a typed record from provider responses, preserve run ID and API URLs, and compare the returned head/base/workflow/candidate identities with a freshly fetched PR snapshot. Unknown or unavailable fields must fail closed. A locally constructed dataclass is not itself an attestation.

The current CI workflow uses `pull_request` without branch filters, and runs `npm run all`. A query for pull-request-triggered workflow runs on commit `f6b4f957e6fdf6c7bac0eeffd4d5d225792c0d95` returned an empty list. That means no matching run was observed through this query; it does not prove no checks of any type exist.

## Great Scale mapping

- **Geometry/state:** current PR snapshot `S=(H,B,W,M)`.
- **Predicate:** internal equality and success checks.
- **Observation boundary:** authoritative provider API response.
- **Provenance boundary:** validate the returned run identity, workflow revision, and candidate metadata.
- **Decision:** accept only when consistency, authenticity, and candidate validity are separately established.

## Verification status

The CLII regression is an abstract contract test, not an API integration test. No full-suite, build, hosted CI pass, or deployment is claimed in this note. The next engineering increment is a small provider adapter plus fixture-backed tests for missing fields, stale PR snapshots, wrong run IDs, workflow revision mismatch, and candidate mismatch.
