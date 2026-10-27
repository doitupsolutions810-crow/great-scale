# Public Repository Integration Registry

This file describes the public-facing subset of the repository integration map. Private repository names and metadata are intentionally excluded.

## Inventory and evidence status

- Data: `integration/repository-map.json`.
- Snapshot date: 2026-10-27.
- Scope: publicly visible repositories only.
- Roles are marked `readme-inspected` only when the public README was inspected in this pass; `inventory-only` means source-level purpose is not established here.
- All listed repositories remain `not-end-to-end-verified` and all edges remain `proposed-not-verified`. These edges express desired contracts, not proof that services are connected.

## Validate locally

```sh
node --test test_system_map.mjs
node tools/validate-repository-map.mjs
npm test
npm run all
```

The validator checks unique repository names, snapshot-count consistency, owner/branch/visibility metadata, interface endpoints, duplicate edges, and evidence requirements before any record may be marked verified.

## Promotion requirement

A verified interface must carry a complete, revision-bound execution proof:

- Full 40-character `sourceCommitSha` and `targetCommitSha` identify both endpoint revisions actually exercised by the integration test.
- `testRepository` names a repository in this public registry; `testCommitSha` is the exact test-harness revision.
- `testRunHeadSha` equals `testCommitSha`; `testRunId` and `testRunAttempt` are positive integers for the observed attempt.
- `testRunUrl` is the canonical URL for that registered repository and run ID, and `testRunConclusion` must be `success`.
- `observedResult` must be `pass`, and `evidenceUrl` must be a durable HTTPS URL within that exact run.

A repository-level `verified` claim uses the same run proof and pins its subject revision with `commitSha`. The validator checks the evidence envelope's consistency; it does **not** fetch the Actions API, verify the run's real head SHA, or independently inspect the test artifact. Those facts still have to be checked before a human or trusted promotion service updates the registry. A well-formed JSON file is not a network integration test. A hosted runner failure without executed steps is not a pass.

## Next step

Keep the public map limited to public repositories. Maintain any complete private inventory only in an access-controlled repository. Refresh the public snapshot as public repositories change, then establish the interface contracts with exact-head integration tests.
