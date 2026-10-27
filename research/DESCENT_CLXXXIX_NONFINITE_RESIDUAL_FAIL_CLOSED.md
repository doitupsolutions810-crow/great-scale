# Descent CLXXXIX — non-finite residual input can masquerade as a safe coordinate

Date: 2026-10-26 / GitHub commit timestamps may roll into 2026-10-27.

## Finding

A deeper source audit of Control Plane PR #33 found the same permissive residual coercion in both `integrate.mjs` and `status/procurement-bridge.mjs`:

```js
const residualS = Number(process.env.GREAT_SCALE_S || 0) || 0;
```

This is not a strict parser. A supplied non-numeric value such as `NaN` is converted to the default coordinate `0`. More seriously, `Infinity` is truthy and survives the expression. In the shared residual module, `coneCompliant(S)` is implemented as `psi(S) >= CONE - 1e-12`; with `S = Infinity`, that comparison is true even though the coordinate is not a finite physical/model input. JSON serialization can then turn non-finite numeric output into `null`, obscuring the invalid input after evaluation.

The failure is a validation-to-authorization gap: malformed input is not rejected at the boundary, and the downstream cone predicate does not itself establish finiteness.

## Formal invariant

Let (s_{raw}) be the supplied environment value and (s) the parsed coordinate.

```
valid(s_raw) := unset(s_raw) OR (nonempty(s_raw) AND finite(Number(s_raw)))
s := 0                         when unset
s := Number(s_raw)             when valid and supplied
authorize := valid(s_raw) AND all_other_gates
```

The key invariant is:

`non-finite or malformed input ⇒ HOLD`

It must not be normalized to `S = 0` or allowed to satisfy a geometric inequality by infinity.

## Mitigation committed to Control Plane PR #33

On branch `fix/mainline-public-evidence-contract-verification`:

- Added `lib/residual-input.mjs` with an explicit parser. Only an unset variable receives the documented default `0`; supplied empty, non-numeric, `NaN`, infinite, or overflow values are invalid.
- Added `test/residual-input.test.mjs` covering defaulting, finite positive/negative values, empty strings, non-numeric input, `NaN`, infinities, and overflow.
- Updated `integrate.mjs` and `status/procurement-bridge.mjs` to pass a fail-closed sentinel into the cone check when parsing fails, emit `HOLD_INVALID_RESIDUAL` or `HOLD_RESIDUAL_CONE`, and report the parse failure explicitly rather than presenting a fabricated residual snapshot.
- Added the new test to the package test command and the focused evidence-contract workflow's path filters, syntax checks, and Node test command.

This prevents invalid residual input from yielding a procurement-ready result through silent coercion. It does not implement a live QGT/topology feed and does not enable production authorization.

## Verification status

- Source updates are committed on PR #33's branch; latest inspected head is `25be705adf58276c32794a508d6b386179071f41`.
- The focused workflow is configured to syntax-check and run the new regression.
- An isolated Node.js 22 runtime run of the parser module and its regression cases passed **6/6 tests**. A separate reproduction confirmed the old coercion maps `NaN`/non-numeric values to zero and allows `Infinity` to satisfy the cone inequality.
- The hosted Actions runner previously failed before exposing any steps. Therefore the newly committed JavaScript test has not yet been proven to execute in hosted CI.
- The local environment cannot clone GitHub (DNS/network unavailable), so a clean-checkout full-suite run was not possible in this pass.
- This finding addresses input validity only; it does not close the E0–E6 versus G0–G6 producer/consumer protocol mismatch, production key pinning, live endpoint verification, or PR history divergence.

Decision: production remains **HOLD**. Source mitigation is committed; runtime integration and exact-head hosted verification remain outstanding.


## Great Scale policy-model integration

Added `test_great_scale_clxxxix_finite_residual_boundary.py` and wired it into the `npm run all` aggregate in this branch. The isolated Python model run passed, covering default/finite values, malformed/non-finite inputs, overflow, and finite cone violation. This is an additional policy-level check, not a substitute for executing the Control Plane JavaScript integration.
