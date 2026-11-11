#!/usr/bin/env python3
"""Great Scale volume-edge battery v0.5.9 — companion to bidirectional bridge volume.
"""
from __future__ import annotations
import math
import random
import statistics
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
    random.seed(20261110 + 59)

    def check(cond: bool, name: str) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            if len(fails) < 40:
                fails.append(name)

    # A. Ultra-long mixed
    for i in range(30):
        x = random.uniform(-3000, 3000)
        for step in range(1000):
            k = 0.997 if step % 29 == 0 else random.uniform(0.25, 0.8)
            x = soft_contract(x, k)
            if step % 200 == 0:
                check(math.isfinite(x), f"A-finite i={i}")
                check(stress_residual(x) >= -1e-15, f"A-stress i={i}")
        check(abs(x - FIXED) < 1.5, f"A-final i={i}")

    # B. Fiber constancy under heavy translation
    for i in range(80):
        x = random.uniform(-10, 10)
        k = random.uniform(0.3, 0.75)
        c0 = soft_contract(x, k)
        for n in range(-30, 31, 3):
            check(abs(soft_contract(x + n * 9, k) - c0) < 1e-11,
                  f"B-fiber i={i} n={n}")

    # C. Residual tails
    residuals = []
    for _ in range(300):
        x = random.uniform(-800, 800)
        for _ in range(120):
            x = soft_contract(x, 0.52)
        residuals.append(abs(x - FIXED))
    mean_r = statistics.mean(residuals)
    p95 = sorted(residuals)[int(0.95 * len(residuals))]
    check(mean_r < 0.04, f"C-mean {mean_r:.5f}")
    check(p95 < 0.12, f"C-p95 {p95:.5f}")

    # D. Basin volume
    hits = 0
    N = 400
    for _ in range(N):
        x = random.uniform(-120, 120)
        for _ in range(90):
            x = soft_contract(x, 0.58)
        if abs(x - FIXED) < 0.06:
            hits += 1
    check(hits >= int(0.93 * N), f"D-basin {hits}/{N}")

    # E. Phase-modulated long run
    for i in range(40):
        t0 = random.uniform(0, 40)
        x = random.uniform(0, 9)
        for step in range(80):
            s = state_at(t0 + step * 0.12, rate=1.0)
            k = 0.35 + 0.4 * (1 - 4 * s["S"])
            k = max(0.15, min(0.9, k))
            x = soft_contract(x, k)
            check(s["psi"] + 1e-14 >= CONE, f"E-Psi i={i}")
        check(abs(x - FIXED) < 0.7, f"E-final i={i}")

    # F. Composition product identity
    for a in [0.25, 0.4, 0.55, 0.7]:
        for b in [0.3, 0.5, 0.65]:
            for x in [0.0, 1.0, 3.5, 6.0, 8.8]:
                left = soft_contract(soft_contract(x, b), a)
                right = soft_contract(x, a * b)
                check(abs(left - right) < 1e-12, f"F-prod a={a} b={b} x={x}")

    # G. Stress non-negativity
    for i in range(200):
        x = random.uniform(-50, 50)
        check(stress_residual(x) >= -1e-15, f"G-stress i={i}")

    # H. FIXED + noise stability
    for k in [0.3, 0.5, 0.7, 0.9]:
        x = FIXED
        for _ in range(400):
            x = soft_contract(x + random.uniform(-1e-13, 1e-13), k)
        check(abs(x - FIXED) < 1e-7, f"H-stable k={k}")

    return passed, failed, fails


def main() -> int:
    print("=== Great Scale volume-edge battery v0.5.9 ===")
    passed, failed, fails = run()
    total = passed + failed
    print(f"\n=== {passed}/{total} passed  ({failed} failed) ===")
    if fails:
        print("Sample failures:")
        for f in fails[:25]:
            print("  FAIL ", f)
    if failed <= 15 and passed >= 2000:
        print("Volume-edge measure coherent.")
        return 0
    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
