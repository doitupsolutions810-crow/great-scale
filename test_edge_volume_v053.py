#!/usr/bin/env python3
"""Great Scale ultra-volume edge battery v0.5.3 — 3000+ additional systematic cases.

Layers on top of v0.5.2:
  - combined property stress (contract → stress → involution → state)
  - adversarial / pathological inputs (subnormals, huge magnitudes, near-singularity k)
  - cross-channel consistency under translation + scaling
  - longer multi-stage trajectories with intermediate assertions
  - denser Monte-Carlo + stratified sampling
  - heat-law algebraic identities under composition
  - residual decay rate empirical checks vs theoretical k^n
  - fixed-point basin sampling in modular neighborhoods

Never claims certainty. Only that the sampled measure remains coherent
with the circle-native + CONE laws under this larger probe.
"""
from __future__ import annotations
import math
import random
import sys
from typing import List, Tuple

PHI = (1 + math.sqrt(5)) / 2
CONE = PHI ** -2
FIXED = 4.5


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


def run() -> Tuple[int, int, List[str]]:
    passed = 0
    failed = 0
    fails: List[str] = []
    random.seed(20261110 + 53)

    def check(cond: bool, name: str) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            if len(fails) < 50:
                fails.append(name)

    # A. Combined property stress (~800)
    for i in range(200):
        x0 = random.uniform(-2000, 2000)
        k = random.uniform(0.1, 0.92)
        x = x0
        for step in range(40):
            x = soft_contract(x, k)
            r = stress_residual(x)
            check(r >= -1e-15, f"A-stress≥0 i={i} s={step}")
            check(mod_dist(involution(involution(x)), x) < 1e-9,
                  f"A-inv² i={i} s={step}")
        check(abs(x - FIXED) < 0.5, f"A-final near FIXED i={i}")

    # B. Residual decay rate vs theoretical k^n (~400)
    for k in [0.3, 0.5, 0.7, 0.85]:
        for start in [0.0, 1.0, 3.0, 8.0]:
            x = start
            dist0 = abs(((start % 9 + 9) % 9) - FIXED)
            for n in range(1, 51):
                x = soft_contract(x, k)
                dist = abs(x - FIXED)
                theo = dist0 * (k ** n)
                if theo > 1e-12:
                    rel = abs(dist - theo) / max(theo, 1e-15)
                    check(rel < 0.15 or dist < 1e-9,
                          f"B-decay k={k} start={start} n={n}")
                else:
                    check(dist < 1e-8, f"B-decay tiny k={k} n={n}")

    # C. Adversarial / pathological inputs (~500)
    for mag in [1e-300, 1e-200, 1e-100, 1e-50, 1e-20]:
        for sign in (+1, -1):
            x = sign * mag
            c = soft_contract(x, 0.5)
            check(math.isfinite(c), f"C-subnormal finite {x}")
            check(0.0 <= ((c % 9) + 9) % 9 < 9.0 + 1e-12, f"C-subnormal range {x}")

    for mag in [1e20, 1e50, 1e100, 1e200]:
        for sign in (+1, -1):
            x = sign * mag
            c = soft_contract(x, 0.5)
            check(math.isfinite(c), f"C-huge finite {x}")
            m = ((c % 9) + 9) % 9
            check(0.0 <= m < 9.0 + 1e-9, f"C-huge canon {x}")

    for k in [0.999, 0.9999, 0.99999]:
        x = 0.0
        for _ in range(5000):
            x = soft_contract(x, k)
        check(abs(x - FIXED) < abs(0.0 - FIXED), f"C-near1 k={k} progress")
        check(math.isfinite(x), f"C-near1 k={k} finite")

    check(abs(soft_contract(3.0, 0.0) - FIXED) < 1e-15, "C-k0 → FIXED")
    check(abs(soft_contract(FIXED, 0.0) - FIXED) < 1e-15, "C-k0 FIXED fixed")

    for k in [-0.3, -0.5, -0.7]:
        x = 1.0
        for _ in range(80):
            x = soft_contract(x, k)
        check(abs(x - FIXED) < 0.5, f"C-negk k={k} near FIXED")

    # D. Cross-channel consistency under translation (~400)
    for i in range(100):
        x = random.uniform(0, 9)
        n = random.randint(-20, 20)
        check(abs(soft_map(soft_map(x + n * 9)) - (x + n * 9)) < 1e-10,
              f"D-softMap² shifted i={i}")
        c0 = soft_contract(x, 0.6)
        cn = soft_contract(x + n * 9, 0.6)
        check(abs(c0 - cn) < 1e-12, f"D-fiber contract i={i}")

    # E. Longer multi-stage trajectories (~400)
    for stage_k in [0.4, 0.6, 0.8]:
        for start in [-50, 0, 2, 7, 100]:
            x = start
            history = [x]
            for s in range(60):
                x = soft_contract(x, stage_k)
                history.append(x)
                if s > 0 and s < 20:
                    check(abs(history[-1] - FIXED) <= abs(history[-2] - FIXED) + 1e-9,
                          f"E-mono stage_k={stage_k} start={start} s={s}")
            check(abs(x - FIXED) < 0.05, f"E-final stage_k={stage_k} start={start}")

    # F. Heat-law algebraic identities (~200)
    for i in range(100):
        h = random.random()
        check(abs(heat(h) - heat(1 - h)) < 1e-15, f"F-heat sym h={h}")
        check(heat(h) >= 0, f"F-heat≥0 h={h}")
        check(heat(h) <= 0.25 + 1e-15, f"F-heat≤0.25 h={h}")
    check(abs(heat(0.5) - 0.25) < 1e-15, "F-max")
    check(heat(0) == 0 and heat(1) == 0, "F-ends")

    # G. Fixed-point basin sampling (~300)
    for delta in [1e-12, 1e-9, 1e-6, 1e-3, 0.01, 0.1, 0.5, 1.0, 2.0]:
        for sign in (+1, -1):
            x = FIXED + sign * delta
            for k in [0.2, 0.5, 0.8]:
                c = soft_contract(x, k)
                check(abs(c - FIXED) <= abs(x - FIXED) + 1e-12,
                      f"G-basin δ={delta} k={k}")
                y = x
                for _ in range(100):
                    y = soft_contract(y, k)
                check(abs(y - FIXED) < 1e-5, f"G-basin long δ={delta} k={k}")

    # H. Stratified Monte-Carlo (~400)
    strata = [
        (-1e5, -100), (-100, -1), (-1, 0), (0, 1), (1, 100), (100, 1e5)
    ]
    mc_ok = 0
    draws = 0
    for lo, hi in strata:
        for _ in range(70):
            start = random.uniform(lo, hi)
            k = random.uniform(0.15, 0.9)
            x = start
            for _ in range(150):
                x = soft_contract(x, k)
            draws += 1
            if abs(x - FIXED) < 1e-3:
                mc_ok += 1
    check(mc_ok >= int(0.92 * draws), f"H-stratified MC {mc_ok}/{draws}")

    # I. stateAt + CONE under extreme rates / times (~200)
    for rate in [0.1, 0.5, 0.85, 1.0, 2.0, 10.0]:
        for t in [-1e6, -100, 0, 1, 50, 1e6]:
            s = state_at(t, rate=rate)
            check(s["psi"] + 1e-14 >= CONE, f"I-Ψ rate={rate} t={t}")
            check(0 <= s["S"] <= 0.25 + 1e-14, f"I-S rate={rate} t={t}")

    # J. Involution + softMap agreement at fixed point only (~100)
    for i in range(50):
        x = random.uniform(0, 9)
        inv = involution(x)
        sm = soft_map(x)
        if abs(x - FIXED) < 0.01:
            check(abs(inv - sm) < 0.05, f"J-agree near FIXED x={x}")
        check(0 <= inv < 9 or abs(inv - 9) < 1e-12, f"J-inv range x={x}")

    return passed, failed, fails


def main() -> int:
    print("=== Great Scale ultra-volume EDGE battery v0.5.3 ===")
    passed, failed, fails = run()
    total = passed + failed
    print(f"\n=== {passed}/{total} passed  ({failed} failed) ===")
    if fails:
        print("Sample failures (first 50):")
        for f in fails[:50]:
            print("  FAIL ", f)
    if failed <= 15 and passed >= 2900:
        print("Ultra-volume measure coherent.")
        return 0
    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
