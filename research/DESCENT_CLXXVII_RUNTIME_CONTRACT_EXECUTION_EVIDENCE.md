# DESCENT CLXXVII — Runtime Contract Alignment and the Execution-Evidence Gap

Date: 2026-10-26

## Finding

The Control Plane root manifest declared Node.js `>=18`, while `platform/package.json` declares `>=20`. The canonical root test script runs:

```text
node test/self-test.mjs && node --test test/evidence-console.test.mjs && npm --prefix platform test
```

The platform test command invokes Node's built-in test runner. Therefore, the root manifest's lower engine floor did not accurately express the runtime required by the complete test path.

## Mitigation committed

On `doitupsolutions810-crow/living-intermediate-control-plane`, PR #31 branch `fix/force-procurement-evidence-auth`, commit:

`e6efc75469a93d033070cdfea40d0559767987c4`

The root `engines.node` value is now `>=20`. The file was fetched again at that exact commit and parsed as JSON. The verification compared the root and platform engine declarations and confirmed the root test script includes the platform test command. This is a manifest-level consistency test, not a full repository test run.

## Important causal limitation

The prior hosted workflow failure (run 40430914384) reported a failed verification job but exposed no steps or logs; job-step retrieval returned an empty list and log retrieval returned `BlobNotFound`. The runtime mismatch is a concrete defect worth correcting, but available evidence does **not** prove it caused that CI failure. Do not state that the root cause is fixed until a successful workflow runs on the exact candidate.

## Great Scale mapping

Let:
- (M): manifest accurately declares requirements of the full test path.
- (R): the required test path is executable in the configured runner.
- (E): committed tests actually execute and pass.
- (P): the result is bound to the exact candidate revision.
- (A): the runner and evidence source are authorized.
- (F): the evidence is fresh.
- (C): required test and gate results are complete.
- (L): the live producer/consumer contract is verified.

The acceptance invariant remains:

[
S=M\land R\land E\land P\land A\land F\land C\land L
]

This patch improves (M), and a static manifest check provides limited evidence for that dimension. It does not prove (R,E,P,A,F,C,L). Overall release readiness therefore remains **HOLD**.

## Next acceptance gates

1. Obtain a usable CI execution on the exact candidate and diagnose any failure from real runner logs.
2. Run the full root `npm test` suite successfully on Node 20+.
3. Run `npm run verify:evidence-console:live` against the intended production endpoint and confirm public authority plus the v5.4.0 trust contract.
4. Independently verify the configured Cosign identity and issuer against the actual trusted workflow certificate.
5. Verify report freshness, revision binding, no-skip behavior, immutable digest, scan/sign/verify consistency, and evidence completeness.
6. Consolidate overlapping PR #29 and PR #31 before any merge.

## Decision

The runtime declaration mismatch is mitigated in source and verified by re-fetching the exact commit. Full test execution and live trust verification remain unproven. Keep PR #31 draft and procurement disabled until all acceptance gates pass.


## Follow-up — root runtime contract executable on PR #29 (2026-10-27)

The same runtime mismatch was found still present on Control Plane PR #29 branch `fix/procurement-evidence-authorization`, whose root manifest was still `>=18`. It is now aligned to `>=20` in commit `cf7088adddfdb14064e08abf6815e7853f8e675f`. A new committed `test/runtime-contract.test.mjs` is included in the root `npm test` script and asserts both the root/platform engine-floor relationship and that the canonical root test command includes the platform suite. The most recent root package update is commit `0dc761bc1ccc38f1d8304236311dcfe2a32d6ba0`.

The isolated runtime-manifest harness passed 2/2 assertions. The exact candidate's latest hosted run [40431955723](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40431955723) still exposes no steps/logs. The manifest defect is mitigated, but it is not established as the cause of CI startup failures; full test execution remains unknown.
