# Great Scale — Levels 8201–8300: one canonical contraction rate across runtimes

## Finding

The ES-module and CommonJS implementations define the default scalar contraction rate as `CONE = φ⁻²`. The Python reference instead defaulted both `soft_contract(x, k)` and `run_descent(start, steps, k)` to `k=0.5`. Both values satisfy `|k| < 1`, so convergence-only tests can pass while the same model follows different trajectories depending on the runtime.

For initial value (x_0=1) and fixed point (x_*=4.5), the declared update is

[
x_{n+1}=x_*+k(x_n-x_*).
]

With (k=phi^{-2}approx0.381966), the first step is approximately (3.163119). With (k=0.5), it is (2.75). This is a deterministic, immediately observable cross-runtime discrepancy, not merely a long-run numerical drift.

## Integration

- Changed Python `soft_contract` and `run_descent` defaults from `0.5` to the already-defined canonical constant `CONE = φ^{-2}`.
- Added regression checks that each public Python default produces the one-step value implied by (k=mathrm{CONE}).
- Kept explicit caller-supplied (k) values supported; this change aligns defaults, not the broader parameter domain.
- The README edit was attempted but not completed; this research note records the canonical default explicitly.

## Mathematics

Subtract the fixed point from both sides:

[
e_{n+1}=x_{n+1}-x_* = k(x_n-x_*)=ke_n.
]

Thus (e_n=k^n e_0), and any (|k|<1) converges to zero. This convergence theorem does not imply that two different valid (k) values produce the same trajectory. Runtime parity requires matching the parameter contract as well as the recurrence form.

## Great Scale mapping

| Level | Mathematics | Science / engineering meaning | Test / verification gate |
|---|---|---|---|
| 8201 | (k_{mathrm{JS}}=mathrm{CONE}=phi^{-2}) | Establish the canonical model default | Inspect ESM and CJS defaults |
| 8210 | (k_{mathrm{Python}}=0.5
ephi^{-2}) | A valid contraction can still violate cross-runtime parity | Compare defaults directly |
| 8220 | (x_1=4.5+k(1-4.5)) | Different defaults diverge on the first transition | Assert the expected first step |
| 8230 | (e_n=k^n e_0) | Shared convergence class does not mean identical dynamics | Keep convergence and parity tests distinct |
| 8240 | (	ext{same model} Rightarrow 	ext{same default contract}) | Published references should implement the same parameter defaults | Python regression and cross-file source audit |

## Test / verify / run / build status

- **Integrated:** Python defaults and two targeted regression checks committed as `aca643f553a097f8b4e8b9d9ea215466da196d02`.
- **Source verification:** the updated file was written through the GitHub contents API. The full updated file has not yet been re-fetched for a post-write review.
- **Execution:** the new checks have not been run in this session. No claim is made that `python3 test_descent.py`, `npm test`, or `npm run all` passed.
- **CI:** latest known exact-branch workflow evidence remains a failed run with no usable step logs/artifact. A new exact-head run must be inspected before declaring execution status.
- **Build:** unverified.
- **Promotion:** keep PR #89 draft/unmerged. Reconcile branch divergence from `main`, and require exact-head tests with retrievable runner logs and a same-run receipt before promotion.

## Science boundary

This finding establishes an implementation-contract inconsistency in a mathematical software model. It is not empirical evidence for a physical mechanism and does not establish a quantum-geometry law.
