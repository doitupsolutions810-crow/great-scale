# Descent LV — CI and repository integration audit

**Status:** confirmed static inspection of the repository workflow; no local runtime tests performed.

## Critical repository finding

The current `.github/workflows/blank.yml` is a starter workflow named `CI`. Its only steps are checkout, `echo Hello, world!`, and two `echo` statements telling the user to add build/test/deploy commands. It does **not** run `npm test`, `python3 test_descent.py`, `npm run all`, lint, type checks, or a production build.

The repository `package.json` declares:
- `npm test`: `node test.js && node test_quantum_geometry.js && node test_topological_qgt.cjs`
- `npm run descent`: `python3 test_descent.py`
- `npm run all`: `npm test && python3 test_descent.py`

Therefore, the existing CI workflow is not a valid test gate for Great Scale, even if its placeholder job were to pass. The observed pull-request run for Descent LV #109 reports a failed `build` job, but the available connector did not return the logs. The cause of that particular failure is unknown; it should not be attributed to this research document without evidence.

## Required CI remediation

Replace the placeholder job with a real workflow that:
1. checks out the tested commit;
2. installs a pinned supported Node.js version;
3. installs Python 3;
4. runs `npm ci` only if a lockfile is committed (otherwise first add/commit a lockfile or use the repository's documented reproducible install procedure);
5. runs `npm test`, `python3 test_descent.py`, and `npm run all` (avoid redundant invocations if CI time matters, but preserve explicit required coverage);
6. fails on any test failure and uploads logs/artifacts as appropriate.

Before implementing that workflow, inspect the repository root for a committed lockfile and dependency declarations. Do not use `npm ci` when no lockfile exists. Do not claim CI verification until a run on the pull-request head completes successfully and the actual test commands appear in its logs.

## Great Scale implications

This is a process-level validity gap: the repository currently advertises a test command, but its CI workflow does not execute that command. Thus a green workflow could not establish that the scientific/math regressions pass. The risk-certificate document is correctly labeled research-only; promotion requires both theorem review and a functioning CI gate.

## Verification record

- Static workflow contents inspected from branch `research/descent-lv-robust-risk-certificate`.
- Static package scripts inspected from the repository default branch.
- GitHub Actions run `40058296394` for PR #109 reported job `build` as `failure`.
- Job-log retrieval returned 404/BlobNotFound; root cause unknown.
- No local build, npm test, Python test suite, deployment, or production experiment is claimed.
