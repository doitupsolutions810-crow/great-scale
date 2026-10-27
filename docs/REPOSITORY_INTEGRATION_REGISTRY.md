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

A verified interface must be backed by the exact commit SHA, an actual test/workflow run, an observed result, and an evidence URL with applicable authority/provenance checks. A well-formed JSON file is not a network integration test. A hosted runner failure without executed steps is not a pass.

## Next step

Keep the public map limited to public repositories. Maintain any complete private inventory only in an access-controlled repository. Refresh the public snapshot as public repositories change, then establish the interface contracts with exact-head integration tests.
