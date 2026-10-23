# Great Scale — Levels 8201–8300: one canonical contraction rate across runtimes

## Finding

The ES-module and CommonJS implementations default to `CONE = φ⁻² ≈ 0.381966`. The Python reference instead defaulted both `soft_contract(x, k)` and `run_descent(start, steps, k)` to `k=0.5`. Both values satisfy `|k| < 1`, so convergence-only tests can pass while the same model follows different trajectories depending on the runtime.

For initial value `x₀ = 1` and fixed point `x* = 4.5`, the declared update is:

`xₙ₊₁ = x* + k(xₙ − x*)`

With `k = φ⁻² ≈ 0.381966`, the first step is approximately `3.163119`. With `k = 0.5`, it is `2.75`. This is a deterministic, immediately observable cross-runtime discrepancy, not merely a long-run numerical drift.

## Integration

- Changed Python `soft_contract` and `run_descent` defaults from `0.5` to the already-defined canonical constant `CONE = φ⁻²`.
- Added regression checks that each Python default produces the one-step value implied by `k=CONE`.
- Kept explicit caller-supplied `k) values supported; this change aligns defaults, not the broader parameter domain.
- A README edit was attempted but not completed; this research note records the canonical default explicitly.

## Mathematics

Subtracting the fixed point gives the error recurrence:

`eₙ₊₁ = xₙ₊₁ − x* = k(xₙ − x*) = k eₙ`

Therefore `eₙ = kⁿ e₀`, and any `|k| < 1` converges to zero. This convergence theorem does not imply that two different valid values of `k` produce the same trajectory. Runtime parity requires matching the parameter contract as well as the recurrence form.

## Great Scale mapping

| Level | Mathematics | Science / engineering meaning | Test / verification gate |
|---|---|---|---|
| 8201 | JavaScript default: `k=CONE=φ⁻²` | Establish the canonical model default | Inspect ESM and CJS defaults |
| 8210 | Python default previously: `k=0.5 ≠ φ⁻²` | A valid contraction can still violate cross-runtime parity | Compare defaults directly |
| 8220 | `x₁=4.5+k(1−4.5)` | Different defaults diverge on the first transition | Assert the expected first step |
| 8230 | `eₙ=kⁿe₀` | Shared convergence class does not mean identical dynamics | Keep convergence and parity tests distinct |
| 8240 | Same model implies same default contract | Published references should implement the same parameter defaults | Python regression and cross-file source audit |

## Test / verify / run / build status

- **Integrated:** Python defaults and two targeted regression checks committed as `aca643f553a097f8b4e8b9d9ea215466da196d02`.
- **Source re-fetch:** the updated `test_descent.py` was fetched back from GitHub; both defaults and both regression checks are present.
- **Execution:** the new checks have not been run in this session. No claim is made that `python3 test_descent.py`, `npm test`, or `npm run all` passed.
- **CI:** no pull-request workflow run was returned for the documentation commit when checked. The latest known run for the earlier head failed without usable step logs or artifacts.
- **Build:** unverified.
- **Promotion:** keep PR #89 draft/unmerged. Reconcile branch divergence from `main`, and require exact-head tests with retrievable runner logs and a same-run receipt before promotion.

## Science boundary

This finding establishes an implementation-contract inconsistency in a mathematical software model. It is not empirical evidence for a physical mechanism and does not establish a quantum-geometry law.
