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
- Added `test/residual-input.test.mjs` covering defaulting, strict decimal notation, finite values within `[0, 0.25]`, empty strings, non-numeric input, `NaN`, infinities, overflow, underflow, and out-of-domain coordinates.
- Updated `integrate.mjs` and `status/procurement-bridge.mjs` to pass a fail-closed sentinel into the cone check when parsing fails, emit `HOLD_INVALID_RESIDUAL`, `HOLD_RESIDUAL_DOMAIN`, or `HOLD_RESIDUAL_CONE`, and report the parse failure explicitly rather than presenting a fabricated residual snapshot.
- Added the new test to the package test command and the focused evidence-contract workflow's path filters, syntax checks, and Node test command.

This prevents invalid residual input from yielding a procurement-ready result through silent coercion. It does not implement a live QGT/topology feed and does not enable production authorization.

## Verification status

- Source updates are committed on PR #33's branch; latest inspected head is `021946b2efaf0bf892e97aede069a26b70164e7b`; GitHub currently reports `mergeable: false`, so integration needs conflict review.
- The focused workflow is configured to syntax-check and run the new regression.
- An isolated Node.js 22 runtime run of the parser module and its regression cases passed **7/7 tests**. A separate reproduction confirmed the old coercion maps `NaN`/non-numeric values to zero and allows `Infinity` to satisfy the cone inequality.
- The hosted Actions runner previously failed before exposing any steps. Therefore the newly committed JavaScript test has not yet been proven to execute in hosted CI.
- The local environment cannot clone GitHub (DNS/network unavailable), so a clean-checkout full-suite run was not possible in this pass.
- This finding addresses input validity only; it does not close the E0–E6 versus G0–G6 producer/consumer protocol mismatch, production key pinning, live endpoint verification, or PR history divergence.

Decision: production remains **HOLD**. Source mitigation is committed; runtime integration and exact-head hosted verification remain outstanding.


## Great Scale policy-model integration

Added `test_great_scale_clxxxix_finite_residual_boundary.py` and wired it into the `npm run all` aggregate in this branch. The isolated Python model run passed, covering default/finite decimal values, malformed/non-finite inputs, overflow/underflow, and out-of-domain values. This is an additional policy-level check, not a substitute for executing the Control Plane JavaScript integration.


## Domain-boundary extension — CLXXXIX-B

The source defines the topology-derived coordinate as `S=(1-tau^2)/4` with `tau` clamped to `[0,1]`; therefore the generated coordinate lies in `[0, 0.25]`. The earlier finite-only parser still allowed large finite values such as `1e100`, for which `coneCompliant(S)` returns true because the predicate is only `CONE + S >= CONE - epsilon`. Those values are finite but outside the coordinate's derivation domain, and downstream residual quantities can become meaningless.

The parser now:
- accepts only decimal numeric notation (not JavaScript-only hexadecimal/binary strings);
- rejects non-finite values, overflow, and nonzero decimal inputs that underflow to numeric zero;
- rejects finite values outside `[0, 0.25]` with `HOLD_RESIDUAL_DOMAIN`;
- preserves the explicit `HOLD_INVALID_RESIDUAL` and `HOLD_RESIDUAL_CONE` paths;
- reports the domain hold in both integrated and procurement-bridge status output.

The expanded isolated Node.js regression suite passed **7/7 tests**, including domain boundaries, malformed strings, overflow/underflow, and out-of-domain finite inputs. These were run against a temporary isolated harness reproducing the committed helper and its residual predicate; this is not a clean checkout of the full repository. Hosted GitHub Actions still fails before exposing steps, so full integration and hosted execution remain unverified.

The new domain bound is derived from the repository's own `fromTopologicalSaturation` formula; if the intended external QGT feed uses a different coordinate convention, that contract must be documented and versioned before widening the accepted domain. Production remains **HOLD**.


## CLXC — the cone predicate is algebraically non-discriminating

Source inspection of `lib/great-scale-residual.mjs` yields:

```
CONE = φ⁻²
psi(S) = CONE + S
coneCompliant(S) := psi(S) >= CONE - 1e-12
```

Substitution reduces the check to `S >= -1e-12`. Consequently, it returns true for `Infinity` and arbitrarily large positive finite values; it cannot independently prove finiteness, domain validity, topology consistency, or producer authority. Under the topology-derived domain `S∈[0,0.25]`, it is true for every accepted value and adds no discriminating power. The actual safety boundary is the strict parser/domain validation, not this cone predicate.

Mitigation:
- Added an explicit warning to the predicate's source comment: it is only a lower-bound predicate, not a finiteness/domain validator or independent geometric proof.
- Added a characterization regression showing the predicate accepts `Infinity` and `1e100`, while the input boundary rejects those values.
- Retained the strict decimal parser, overflow/underflow rejection, and topology-derived domain hold.
- Did not invent a replacement geometric inequality. A stronger cone test requires the authoritative mathematical contract and expected valid/invalid examples from the model owner.

The isolated Node.js suite must be rerun after this additional characterization test. Hosted Actions still fails before exposing execution steps. Production remains **HOLD**.
