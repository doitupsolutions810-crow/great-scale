#!/usr/bin/env python3
"""Great Scale descent test v0.4.2 — soft contraction, involution, stress residual."""
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
    return FIXED + k * (x - FIXED)

def soft_map(x):
    return 9 - x

def stress_residual(x):
    return abs(x - involution(x))

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
    print("=== Great Scale descent test v0.4.2 ===")
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

    checks.append(("heat max 0.25", abs(heat(0.5) - 0.25) < 1e-12))
    checks.append((f"CONE floor {CONE:.4f}", abs(CONE - 0.382) < 1e-3))

    ok = all(abs(soft_map(soft_map(x)) - x) < 1e-9 for x in [0, 1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9])
    checks.append(("softMap involution-respecting", ok))

    checks.append(("softMap(4.5)=4.5", abs(soft_map(4.5) - 4.5) < 1e-9))

    s = state_at(0)
    checks.append(("stateAt Ψ ≥ CONE", s["psi"] + 1e-12 >= CONE))
    checks.append(("stateAt λ may be < CONE at low heat", s["lam"] < CONE or s["S"] > 0.1))

    # GS-LVI seam: quotient-circle contraction
    # Public docs describe a modulo-nine circle with involution, but
    # soft_contract is an affine map on the real line. On the quotient,
    # C(x+9n) - C(x) = 9kn, a multiple of 9 only when k is an integer.
    # Under |k|<1 the only integer is k=0, so the circle fiber is
    # non-constant: equivalent states (0 and 9) map to non-equivalent outputs.
    c0, c9 = soft_contract(0), soft_contract(9)
    qd = mod_dist(c0, c9)
    checks.append((f"quotient seam C(0)={c0}, C(9)={c9}, dist={qd:.4f}",
                   abs(qd - 4.5) < 1e-9 and abs(c0 - c9) % 9 > 1e-9))
    # strict |k|<1 admits no nonzero integer k → circle fiber non-constant
    checks.append(("affine map not circle-native under |k|<1",
                   abs(soft_contract(0, 0.5) - soft_contract(9, 0.5)) > 1e-9))

    # softMap collapse: k=0.5 → constant 4.5, cannot preserve two-cycles
    # soft_map(x) = 9-x is a different involution than soft_contract's
    # fixed-point attractor; they agree only at 4.5.
    checks.append(("softMap(2) diverges from soft_contract(2) (collapse check)",
                   abs(soft_map(2) - soft_contract(2)) > 1e-9))
    checks.append(("softMap(2)=7.0 (pure involution, not fixed-point sink)",
                   abs(soft_map(2) - 7.0) < 1e-9))

    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")

    fails = sum(1 for _, ok in checks if not ok)
    print(f"\n=== {len(checks) - fails}/{len(checks)} passed ===")
    return 0 if fails == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
