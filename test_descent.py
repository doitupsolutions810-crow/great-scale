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

def soft_contract(x, k=CONE):
    return FIXED + k * (x - FIXED)

def soft_map(x):
    return 9 - x

def stress_residual(x):
    return mod_dist(x, involution(x))

def run_descent(start=1.0, steps=40, k=CONE):
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
    checks.append(("stress residual is zero at circle-equivalent boundary 0≡9",
                   stress_residual(0) < 1e-9 and stress_residual(9) < 1e-9))
    checks.append(("stress residual is periodic under x→x+9",
                   abs(stress_residual(1.25) - stress_residual(10.25)) < 1e-9))

    checks.append(("heat max 0.25", abs(heat(0.5) - 0.25) < 1e-12))
    checks.append((f"CONE floor {CONE:.4f}", abs(CONE - 0.382) < 1e-3))
    expected_first = FIXED + CONE * (1.0 - FIXED)
    checks.append(("soft_contract default uses CONE",
                   abs(soft_contract(1.0) - expected_first) < 1e-12))
    checks.append(("run_descent default uses CONE",
                   abs(run_descent(steps=1)[-1] - expected_first) < 1e-12))

    # Levels 8301–8308: trajectory equivalence is stronger than convergence
    def closed_form(start, n, k=CONE):
        return FIXED + (k ** n) * (start - FIXED)

    for start in [0.0, 1.0, 4.5, 8.75]:
        trail = run_descent(start=start, steps=12)
        formula_ok = all(abs(trail[n] - closed_form(start, n)) < 1e-12
                         for n in range(13))
        checks.append((f"closed-form trajectory start={start}", formula_ok))

    x0 = 1.25
    x_m = run_descent(start=x0, steps=4)[-1]
    composed = run_descent(start=x_m, steps=7)[-1]
    direct = run_descent(start=x0, steps=11)[-1]
    checks.append(("contraction semigroup T^7(T^4(x)) = T^11(x)",
                   abs(composed - direct) < 1e-12))

    default_trail = run_descent(start=1.0, steps=12)
    explicit_trail = run_descent(start=1.0, steps=12, k=CONE)
    checks.append(("default and explicit canonical trajectories agree",
                   all(abs(a - b) < 1e-12 for a, b in zip(default_trail, explicit_trail))))

    alternate_trail = run_descent(start=1.0, steps=12, k=0.5)
    alternate_converges = abs(alternate_trail[-1] - FIXED) < 1e-2
    alternate_matches = all(abs(a - b) < 1e-12
                            for a, b in zip(default_trail, alternate_trail))
    checks.append(("convergence does not imply trajectory parity",
                   alternate_converges and not alternate_matches))

    ok = all(abs(soft_map(soft_map(x)) - x) < 1e-9 for x in [0, 1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9])
    checks.append(("softMap involution-respecting", ok))

    checks.append(("softMap(4.5)=4.5", abs(soft_map(4.5) - 4.5) < 1e-9))

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
