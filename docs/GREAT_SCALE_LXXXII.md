# Great Scale LXXXII — Calibration Validity and Assumption Drift

## Pinned finding
A result certificate inherits the assumptions of its calibration. If those assumptions cease to be supported, downstream certificates that depend on them must be marked stale and re-evaluated. Reliability requires both certification and revocation.

## Bounded-residual mathematics
Let observed calibration residual be r, with a known deterministic bound |r - r_true| <= u, and allowable true residual B > 0. Define L = max(0, |r| - u) and U = |r| + u.

- If U < B, the whole admissible interval is within tolerance: VALID.
- If L > B, the whole interval exceeds tolerance: INVALID.
- Otherwise the interval overlaps or touches the boundary: DEGRADED / INDETERMINATE.

Equality is not accepted as safe. This is deterministic only if u is a valid bound, the reference is trustworthy, and relevant systematic effects are covered. It is not a statistical confidence interval.

## Transition policy
A decisive breach invalidates immediately. A borderline interval resets the clean streak. Recovery requires K consecutive clean checks. Explicit recalibration increments a provenance version and returns the monitor to DEGRADED; it does not certify itself. Repeated correlated checks are not automatically independent evidence.

## Certificate inheritance
Derived certificates should record calibration version and upstream certificate IDs. When a calibration version becomes invalid or is superseded, dependent certificates become stale / need revalidation; retain their history. This module implements decisions and a version counter, not a full provenance graph.

## Great Scale mapping
- LXXX: observation certificate — can an observation establish a side of a reference?
- LXXXI: bias floor — can more observations ever make the claim certifiable?
- LXXXII: calibration validity — does the bound itself remain defensible?

## Mathematics versus science
The interval classification follows from the stated bound. Whether a real instrument's uncertainty bound is valid requires empirical calibration, independent reference checks, drift monitoring, and domain-specific validation. Unit tests check software behavior, not sensor accuracy or scientific validity.
