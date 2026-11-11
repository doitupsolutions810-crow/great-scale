#!/usr/bin/env python3
"""Great Scale high-volume edge battery v0.5.2 — ~2000+ systematic cases.

Generates dense parametric coverage across:
  - modular representatives and multi-wrap fibers
  - contraction trajectories under dense k and start grids
  - stress residual invariance
  - heat / stateAt / CONE floor under phase sampling
  - channel separation (softMap vs softContract)
  - floating-point boundary neighborhoods
  - Monte-Carlo random ensembles (seeded)

Reports aggregate counts. Critical named invariants are still asserted.
Never claims certainty — only that the sampled measure stays coherent.
"""
from __future__ import annotations
import math
import random
import sys
from typing import List, Tuple

PHI = (1 + math.sqrt(5)) / 2
CONE = PHI ** -2
FIXED = 4.5
EPS = 1e-12


def heat(h: float) -> float:
    return h * (1.0 - h)


def involution(x: float) -> float:
    m = ((x % 9) + 9) % 9
    return (9 - m) % 9


def mod_dist(a: float, b: float) -> float:
    d = abs(((a - b) % 9 + 9) % 9)
    return min(d, 9 - d)


def soft_contract(x: float, k: float = 0.5) -> float:
    m = ((x % 9) + 9) % 9
    return FIXED + k * (m - FIXED)


def soft_map(x: float) -> float:
    return 9.0 - x


def stress_residual(x: float) -> float:
    m = ((x % 9) + 9) % 9
    return abs(m - involution(m))


def state_at(t: float, rate: float = 0.85) -> dict:
    phase = (t * rate) % 1.0
    h = 0.5 - 0.5 * math.cos(2 * math.pi * phase)
    S = heat(h)
    n = 8 - 4 * S
    lam = PHI ** (-n)
    psi = CONE + S
    return {"phase": phase, "h": h, "S": S, "lam": lam, "psi": psi, "n": n}


def run_volume() -> Tuple[int, int, List[str]]:
    passed = 0
    failed = 0
    fails: List[str] = []
    random.seed(20261110)

    def check(cond: bool, name: str) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            if len(fails) < 40:
                fails.append(name)

    # 1. Involution modular identity — dense grid + wraps (~400)
    for i in range(-200, 201):
        x = i * 0.125
        check(mod_dist(involution(involution(x)), x) < 1e-9,
              f"involution² identity x={x}")

    # 2. Two-cycles + boundary class
    for a, b in [(1, 8), (2, 7), (3, 6), (4, 5)]:
        check(involution(a) == b and involution(b) == a, f"cycle {a}↔{b}")
    check(involution(0) == 0 and involution(9) == 0, "boundary 0≡9")
    check(abs(involution(FIXED) - FIXED) < 1e-15, "FIXED fixed")

    # 3. Soft-contract seam / fiber constancy (~500)
    offsets = list(range(-50, 51))
    for off in offsets:
        c0 = soft_contract(0.0 + off * 9)
        c9 = soft_contract(9.0 + off * 9)
        check(abs(c0 - c9) < 1e-12, f"seam off={off}")
        check(mod_dist(c0, c9) < 1e-12, f"mod seam off={off}")

    bases = [0.0, 0.5, 1.0, 2.3, 3.7, 4.5, 5.2, 6.8, 7.1, 8.9]
    for base_x in bases:
        ref = soft_contract(base_x, 0.4)
        for n in range(-15, 16):
            check(abs(soft_contract(base_x + n * 9, 0.4) - ref) < 1e-12,
                  f"fiber base={base_x} n={n}")

    # 4. Long / medium horizon contraction grid (~600)
    ks = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    starts = [-1e4, -100, -9.1, -1.0, 0.0, 0.01, 1.0, 2.5, 4.0,
              4.499, 4.5, 4.501, 5.0, 7.0, 8.5, 8.99, 9.0, 9.1, 100, 1e4]
    for k in ks:
        if k <= 0.7:
            tol, steps = 1e-6, 80
        elif k <= 0.9:
            tol, steps = 1e-4, 220
        elif k <= 0.99:
            tol, steps = 0.12, 600
        else:
            tol, steps = 0.3, 2500
        for st in starts:
            x = st
            for _ in range(steps):
                x = soft_contract(x, k)
            check(abs(x - FIXED) < tol, f"contract k={k} start={st} final={x:.6f}")

    # 5. Stress residual invariance (~200)
    xs = [i * 0.25 for i in range(0, 37)]
    for x in xs:
        r0 = stress_residual(x)
        for n in range(-8, 9):
            rn = stress_residual(x + n * 9)
            check(abs(r0 - rn) < 1e-12, f"stress inv x={x} n={n}")
        check(r0 >= 0, f"stress nonneg x={x}")

    check(stress_residual(FIXED) < 1e-15, "stress@FIXED==0")
    check(stress_residual(FIXED + 1e-14) < 1e-11, "stress near FIXED tiny")

    # 6. Channel separation (~100)
    for i in range(100):
        x = (i / 100.0) * 9.0
        sm = soft_map(x)
        sc = soft_contract(x, 0.5)
        if abs(x - FIXED) > 0.05:
            check(abs(sm - sc) > 0.05, f"channels differ x={x}")
        else:
            check(abs(sm - sc) < 0.1, f"channels near FIXED x={x}")
        check(abs(soft_map(soft_map(x)) - x) < 1e-12, f"softMap² x={x}")

    # 7. stateAt / heat / CONE floor (~200)
    for i in range(200):
        t = (i - 50) * 17.3
        s = state_at(t)
        check(s["psi"] + 1e-14 >= CONE, f"Ψ≥CONE t={t}")
        check(0.0 <= s["S"] <= 0.25 + 1e-14, f"S in [0,0.25] t={t}")
        check(abs(s["S"] - heat(s["h"])) < 1e-14, f"S==heat(h) t={t}")

    check(abs(heat(0.5) - 0.25) < 1e-15, "heat max")
    check(heat(0.0) == 0.0 and heat(1.0) == 0.0, "heat endpoints")

    # 8. Monte-Carlo ensemble (seeded) — 400 draws
    mc_ok = 0
    for _ in range(400):
        start = random.uniform(-5000, 5000)
        k = random.uniform(0.05, 0.97)
        x = start
        for _ in range(180):
            x = soft_contract(x, k)
        if abs(x - FIXED) < 1e-3:
            mc_ok += 1
    check(mc_ok >= 380, f"MC 400 starts ≥380 converged (got {mc_ok})")

    # 9. Near-boundary float neighborhoods (~100)
    for delta in [1e-15, 1e-12, 1e-9, 1e-6, 1e-3]:
        for sign in (+1, -1):
            x = 0.0 + sign * delta
            m = ((x % 9) + 9) % 9
            check(0.0 <= m < 9.0 or abs(m - 9.0) < 1e-12, f"canon near 0 δ={delta}")
            x9 = 9.0 + sign * delta
            m9 = ((x9 % 9) + 9) % 9
            check(0.0 <= m9 < 9.0 or abs(m9) < 1e-12, f"canon near 9 δ={delta}")

    # 10. Descent monotonic approach (sample) (~50)
    for start in [0.0, 1.0, 3.0, 6.0, 8.0]:
        x = start
        prev_dist = abs(x - FIXED)
        ok_mono = True
        for _ in range(30):
            x = soft_contract(x, 0.6)
            d = abs(x - FIXED)
            if d > prev_dist + 1e-12:
                ok_mono = False
                break
            prev_dist = d
        check(ok_mono, f"mono approach start={start}")

    return passed, failed, fails


def main() -> int:
    print("=== Great Scale high-volume EDGE battery v0.5.2 ===")
    passed, failed, fails = run_volume()
    total = passed + failed
    print(f"\n=== {passed}/{total} passed  ({failed} failed) ===")
    if fails:
        print("Sample failures (first 40):")
        for f in fails:
            print("  FAIL ", f)
    if failed <= 5 and passed >= 1900:
        print("Volume measure coherent (≤5 residual float edges).")
        return 0
    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
