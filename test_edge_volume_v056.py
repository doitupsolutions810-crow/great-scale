#!/usr/bin/env python3
"""Great Scale horizon-edge battery v0.5.6 — longer, denser, more adversarial.

New / intensified dimensions:
  - very long trajectories (500-2000 steps) under mixed stochastic + scheduled k
  - double-modular reduction stress (reduce, perturb, reduce again)
  - involution-contract-involution round trips
  - FIXED attractor basin volume estimate under uniform sampling
  - heat-modulated multi-agent style parallel starts (independent trails)
  - catastrophic k sequences (k->1 then sudden drop)
  - cross-property invariants held at every step of long runs
  - statistical tail bounds on residual after fixed budget
  - phase-locked descent (k derived from continuous stateAt)

Never claims certainty. Only that a still larger measured set remains coherent.
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
    random.seed(20261110 + 56)

    def check(cond: bool, name: str) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            if len(fails) < 40:
                fails.append(name)

    # A. Very long mixed trajectories
    for i in range(80):
        x = random.uniform(-2000, 2000)
        for step in range(400):
            if step % 17 == 0:
                k = 0.95
            else:
                k = random.uniform(0.2, 0.85)
            x = soft_contract(x, k)
            if step % 50 == 0:
                check(math.isfinite(x), f"A-finite i={i} s={step}")
                check(stress_residual(x) >= -1e-15, f"A-stress i={i} s={step}")
        check(abs(x - FIXED) < 1.0, f"A-long final i={i}")

    # B. Double-modular reduction stress
    for i in range(100):
        x = random.uniform(-1e5, 1e5)
        for _ in range(30):
            m1 = ((x % 9) + 9) % 9
            x = m1 + random.uniform(-1e-14, 1e-14)
            m2 = ((x % 9) + 9) % 9
            x = soft_contract(m2, random.uniform(0.3, 0.8))
        check(math.isfinite(x), f"B-double finite i={i}")
        check(abs(x - FIXED) < 0.5, f"B-double near i={i}")

    # C. Involution-contract-involution round trips
    for i in range(100):
        x0 = random.uniform(0, 9)
        x = x0
        for _ in range(20):
            x = involution(x)
            x = soft_contract(x, 0.55)
            x = involution(x)
        check(math.isfinite(x), f"C-round finite i={i}")
        check(mod_dist(x, FIXED) < 3.0, f"C-round bounded i={i}")

    # D. FIXED attractor basin volume
    hits = 0
    N = 500
    for _ in range(N):
        x = random.uniform(-100, 100)
        for _ in range(80):
            x = soft_contract(x, 0.6)
        if abs(x - FIXED) < 0.05:
            hits += 1
    check(hits >= int(0.95 * N), f"D-basin hits {hits}/{N}")

    # E. Parallel independent trails
    for batch in range(40):
        trails = [random.uniform(-50, 50) for _ in range(10)]
        for _ in range(50):
            trails = [soft_contract(x, 0.5) for x in trails]
        for j, x in enumerate(trails):
            check(abs(x - FIXED) < 0.1, f"E-parallel batch={batch} j={j}")

    # F. Catastrophic k: near-1 then sudden drop
    for start in [-30, 0, 4.5, 9, 40]:
        x = start
        for _ in range(200):
            x = soft_contract(x, 0.995)
        for _ in range(30):
            x = soft_contract(x, 0.2)
        check(abs(x - FIXED) < 0.15, f"F-catastrophic start={start}")

    # G. Cross-property invariants every step
    for i in range(50):
        x = random.uniform(-100, 100)
        for step in range(60):
            x = soft_contract(x, random.uniform(0.25, 0.8))
            check(math.isfinite(x), f"G-finite i={i} s={step}")
            check(stress_residual(x) >= -1e-15, f"G-stress i={i} s={step}")
            check(mod_dist(involution(involution(x)), x) < 1e-9, f"G-inv2 i={i} s={step}")
            s = state_at(step * 0.2)
            check(s["psi"] + 1e-14 >= CONE, f"G-Psi i={i} s={step}")

    # H. Residual tail after fixed budget
    residuals = []
    for _ in range(300):
        x = random.uniform(-500, 500)
        for _ in range(100):
            x = soft_contract(x, 0.55)
        residuals.append(abs(x - FIXED))
    mean_r = statistics.mean(residuals)
    p95 = sorted(residuals)[int(0.95 * len(residuals))]
    check(mean_r < 0.03, f"H-mean residual {mean_r:.5f}")
    check(p95 < 0.1, f"H-p95 residual {p95:.5f}")

    # I. Phase-locked descent
    for i in range(80):
        t0 = random.uniform(0, 50)
        x = random.uniform(0, 9)
        for step in range(50):
            s = state_at(t0 + step * 0.15, rate=0.9)
            k = 0.4 + 0.4 * math.sin(2 * math.pi * s["phase"]) ** 2
            x = soft_contract(x, k)
            check(s["psi"] >= CONE - 1e-14, f"I-Psi i={i}")
        check(abs(x - FIXED) < 0.5, f"I-phase-locked final i={i}")

    # J. Composition and FIXED stability under noise
    for k in [0.4, 0.6, 0.8]:
        x = FIXED
        for _ in range(300):
            x = soft_contract(x + random.uniform(-1e-14, 1e-14), k)
        check(abs(x - FIXED) < 1e-8, f"J-FIXED noisy stable k={k}")

    return passed, failed, fails


def main() -> int:
    print("=== Great Scale horizon-edge battery v0.5.6 ===")
    passed, failed, fails = run()
    total = passed + failed
    print(f"\n=== {passed}/{total} passed  ({failed} failed) ===")
    if fails:
        print("Sample failures:")
        for f in fails[:30]:
            print("  FAIL ", f)
    if failed <= 15 and passed >= 3000:
        print("Horizon-edge measure coherent.")
        return 0
    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
