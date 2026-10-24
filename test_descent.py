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

def fixed_moment_log_envelope(p, v, b, a=1.0):
    """Sharp fixed-(p,v) witness expectation for f(x)=-a*ln(1-x)."""
    if not (0 <= p < b < 1) or not (0 <= v <= p * (b - p)) or a <= 0:
        raise ValueError("infeasible fixed-moment log-envelope parameters")
    c = p - v / (b - p)
    alpha = v / (((b - p) ** 2) + v)
    loss_c = -a * math.log1p(-c)
    loss_b = -a * math.log1p(-b)
    return c, alpha, (1 - alpha) * loss_c + alpha * loss_b

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

    # Descent LV asymptotic audit: p=1/2, v=1/20, b=1-delta -> 1.
    p, v = 0.5, 0.05
    c_inf = p - v / (1.0 - p)
    alpha_inf = v / (((1.0 - p) ** 2) + v)
    L = -math.log(0.6)
    offset_inf = (5.0 / 6.0) * L
    checks.append(("LV exact interior-atom limit c∞=2/5", abs(c_inf - 0.4) < 1e-15))
    checks.append(("LV exact boundary-atom limit α∞=1/6", abs(alpha_inf - (1.0 / 6.0)) < 1e-15))
    checks.append(("LV exact finite offset (5/6)(-ln 0.6)", abs(offset_inf - 0.42568801980499227) < 1e-14))

    delta = 1e-4
    c_d, alpha_d, u_d = fixed_moment_log_envelope(p, v, 1.0 - delta)
    leading_d = (1.0 / 6.0) * math.log(1.0 / delta)
    remainder_d = u_d - leading_d - offset_inf
    remainder_asymptotic = (
        (5.0 / 9.0) * delta * math.log(1.0 / delta)
        - ((5.0 / 9.0) * L + 5.0 / 18.0) * delta
    )
    ratio_d = u_d / leading_d
    checks.append(("LV finite-δ reference U*(1e-4)≈1.9612003866", abs(u_d - 1.961200386616878) < 1e-11))
    checks.append(("LV finite-δ leading-log ratio is named correctly", abs(ratio_d - 1.2776077587213512) < 1e-10 and abs(ratio_d - 2.25) > 0.5))
    checks.append(("LV post-offset remainder follows δ log(1/δ) expansion", abs(remainder_d - remainder_asymptotic) < 2e-7))

    delta_coarse = 1e-4
    delta_fine = 1e-6
    _, _, u_coarse = fixed_moment_log_envelope(p, v, 1.0 - delta_coarse)
    _, _, u_fine = fixed_moment_log_envelope(p, v, 1.0 - delta_fine)
    q_coarse = (u_coarse - offset_inf) / math.log(1.0 / delta_coarse)
    q_fine = (u_fine - offset_inf) / math.log(1.0 / delta_fine)
    checks.append(("LV offset-corrected coefficient approaches 1/6", abs(q_fine - 1.0 / 6.0) < abs(q_coarse - 1.0 / 6.0)))

    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")

    fails = sum(1 for _, ok in checks if not ok)
    print(f"\n=== {len(checks) - fails}/{len(checks)} passed ===")
    return 0 if fails == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
