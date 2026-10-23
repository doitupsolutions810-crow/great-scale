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

def canonicalize_circle_coordinate(x):
    if not math.isfinite(x):
        raise ValueError("circle coordinate must be finite")
    return ((x % 9) + 9) % 9

def soft_contract(x, k=0.5):
    if not math.isfinite(x):
        raise ValueError("contraction coordinate must be finite")
    if not math.isfinite(k) or abs(k) >= 1:
        raise ValueError("contraction factor k must be finite and satisfy |k| < 1")
    return FIXED + k * (x - FIXED)

def soft_map(x):
    return 9 - x

def stress_residual(x):
    # Same circular metric as the JavaScript/CommonJS runtime.
    return mod_dist(x, involution(x))

def run_descent(start=1.0, steps=40, k=0.5):
    x = canonicalize_circle_coordinate(start)
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

    fixed = [x for x in [i * 0.25 for i in range(36)] if mod_dist(involution(x), x) < 1e-9]
    checks.append(("circle involution fixed points are 0 and 4.5", fixed == [0.0, 4.5]))

    checks.append(("circular residual vanishes at both fixed points", stress_residual(0) < 1e-9 and stress_residual(4.5) < 1e-9))
    checks.append(("circular residual periodicity", all(abs(stress_residual(x) - stress_residual(x + 9)) < 1e-9 for x in [-9.25, 0, 1, 4.5, 8.99])))
    checks.append(("circular residual sample values", all(abs(stress_residual(x) - expected) < 1e-9 for x, expected in [(0, 0), (1, 2), (2, 4), (4, 1), (4.5, 0), (8, 2), (9, 0)])))

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

    checks.append(("circle starts canonicalize 0 ≡ 9", canonicalize_circle_coordinate(0) == canonicalize_circle_coordinate(9) == 0))
    checks.append(("out-of-range circle starts normalize", canonicalize_circle_coordinate(19) == 1))
    rejected = True
    for bad_k in [-2, -1, 1, 2, float("nan"), float("inf"), float("-inf")]:
        try: soft_contract(1, bad_k); rejected = False
        except ValueError: pass
    checks.append(("contraction rejects |k| ≥ 1 and non-finite k", rejected))
    try: soft_contract(float("nan"), 0.5); finite_x_rejected = False
    except ValueError: finite_x_rejected = True
    checks.append(("contraction rejects non-finite x", finite_x_rejected))

    s = state_at(0)
    checks.append(("stateAt Ψ ≥ CONE", s["psi"] + 1e-12 >= CONE))
    checks.append(("stateAt λ may be < CONE at low heat", s["lam"] < CONE or s["S"] > 0.1))

    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")

    fails = sum(1 for _, ok in checks if not ok)
    print(f"\n=== {len(checks) - fails}/{len(checks)} passed ===")
    return 0 if fails == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
