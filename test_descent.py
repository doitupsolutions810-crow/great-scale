#!/usr/bin/env python3
"""Great Scale descent test v0.5.0 — circle-native soft contraction.

GS-LVII: soft_contract now canonicalizes its input to [0,9) before the
affine step, making it a well-defined map on the quotient R/9Z. The
involution, mod_dist, and stress_residual already operated on canonical
representatives; the contraction was the only channel mixing raw real-line
coordinates with modular state. All four now share one state-space
semantics.
"""
import math

PHI = (1 + math.sqrt(5)) / 2
CONE = PHI ** -2
FIXED = 4.5


def heat(h):
    return h * (1 - h)


def involution(x):
    m = ((x % 9) + 9) % 9
    return (9 - m) % 9


def mod_dist(a, b):
    d = abs(((a - b) % 9 + 9) % 9)
    return min(d, 9 - d)


def soft_contract(x, k=0.5):
    """Circle-native contraction: canonicalize to [0,9) then affine step.

    C_k(x) = 4.5 + k * ((x mod 9) - 4.5).  For this to descend to R/9Z
    we need C_k(x+9n) = C_k(x) for all n, which holds precisely because
    the input is projected before scaling. Under |k|<1 the only integer k
    is 0, so a nontrivial quotient contraction must be built this way —
    not by applying a real-line affine formula to raw coordinates.
    """
    m = ((x % 9) + 9) % 9
    return FIXED + k * (m - FIXED)


def soft_map(x):
    """Pure involution channel: 9 - x.  Agrees with soft_contract only at 4.5."""
    return 9 - x


def stress_residual(x):
    """|x - f(x)| on the canonical representative."""
    m = ((x % 9) + 9) % 9
    return abs(m - involution(m))


def run_descent(start=1.0, steps=40, k=0.5):
    x = start
    trail = [x]
    for _ in range(steps):
        x = soft_contract(x, k)
        trail.append(x)
    return trail


def state_at(t, rate=0.85):
    phase = (t * rate) % 1
    h = 0.5 - 0.5 * math.cos(2 * math.pi * phase)
    S = heat(h)
    n = 8 - 4 * S
    lam = PHI ** (-n)
    psi = CONE + S
    return {"phase": phase, "h": h, "S": S, "lam": lam, "psi": psi}


def main():
    print("=== Great Scale descent test v0.5.0 ===")
    checks = []

    ok = all(mod_dist(involution(involution(x)), x) < 1e-9 for x in [i * 0.25 for i in range(37)])
    checks.append(("involution modular identity", ok))

    ok = all(involution(a) == b and involution(b) == a for a, b in [(1, 8), (2, 7), (3, 6), (4, 5)])
    checks.append(("two-cycles preserved", ok))

    ok = involution(0) == 0 and involution(9) == 0
    checks.append(("involution boundary 0≡9 → 0", ok))

    for start in [1.0, 0.5, 8.0, 3.0, 6.5]:
        trail = run_descent(start=start, steps=40)
        conv = abs(trail[-1] - FIXED) < 1e-6
        checks.append((f"descent {start} → {trail[-1]:.6f}", conv))

    r = stress_residual(4.5)
    checks.append((f"stress residual at 4.5 = {r:.6f}", r < 1e-9))

    r2 = stress_residual(2.0)
    checks.append((f"stress residual at 2.0 = {r2:.4f} (>0.5)", r2 > 0.5))

    # GS-LVII: stress residual must be representation-invariant
    checks.append(("stress_residual(2) == stress_residual(11) (quotient invariant)",
                   abs(stress_residual(2) - stress_residual(11)) < 1e-9))

    checks.append(("heat max 0.25", abs(heat(0.5) - 0.25) < 1e-12))
    checks.append((f"CONE floor {CONE:.4f}", abs(CONE - 0.382) < 1e-3))

    ok = all(abs(soft_map(soft_map(x)) - x) < 1e-9 for x in [0, 1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9])
    checks.append(("softMap involution-respecting", ok))

    checks.append(("softMap(4.5)=4.5", abs(soft_map(4.5) - 4.5) < 1e-9))

    s = state_at(0)
    checks.append(("stateAt Ψ ≥ CONE", s["psi"] + 1e-12 >= CONE))
    checks.append(("stateAt λ may be < CONE at low heat", s["lam"] < CONE or s["S"] > 0.1))

    # GS-LVII seam: quotient-circle contraction (FIXED)
    # Circle-native soft_contract canonicalizes before scaling, so
    # equivalent inputs produce identical outputs.
    c0, c9 = soft_contract(0), soft_contract(9)
    qd = mod_dist(c0, c9)
    checks.append((f"quotient seam C(0)={c0}, C(9)={c9}, dist={qd:.4f} (must be ~0)",
                   abs(qd) < 1e-9 and abs(c0 - c9) < 1e-9))
    # fiber constancy across a wider seam
    checks.append(("C(4.5) == C(13.5) (fiber constant, k=0.5)",
                   abs(soft_contract(4.5, 0.5) - soft_contract(13.5, 0.5)) < 1e-9))
    checks.append(("C(-4.5) == C(4.5) (negative seam)",
                   abs(soft_contract(-4.5, 0.5) - soft_contract(4.5, 0.5)) < 1e-9))

    # Channel naming: softMap is pure involution, soft_contract is contraction.
    # They agree only at the fixed point.
    checks.append(("softMap(2)=7.0 (pure involution channel)",
                   abs(soft_map(2) - 7.0) < 1e-9))
    checks.append(("soft_contract(2)=3.75 (contraction channel, distinct from involution)",
                   abs(soft_contract(2, 0.5) - 3.75) < 1e-9))
    checks.append(("channels agree only at fixed point: softMap(4.5)==soft_contract(4.5)",
                   abs(soft_map(4.5) - soft_contract(4.5, 0.5)) < 1e-9))

    # GS-XCV: quotient fiber constancy does not imply topological continuity.
    # The canonicalized values at x=0 and x=9 agree, but the left-hand
    # limit as x approaches 9 is separated from the seam value on S^1_9.
    eps = 1e-6
    seam_value = soft_contract(0.0, 0.5)
    left_value = soft_contract(9.0 - eps, 0.5)
    seam_gap = mod_dist(left_value, seam_value)
    checks.append(("quotient seam left-limit approaches 6.75",
                   abs(left_value - 6.75) < 1e-6))
    checks.append(("quotient seam is discontinuous for k=0.5 (gap approaches 4.5)",
                   abs(seam_gap - 4.5) < 1e-6 and seam_gap > 4.49))

    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")

    fails = sum(1 for _, ok in checks if not ok)
    print(f"\n=== {len(checks) - fails}/{len(checks)} passed ===")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
