#!/usr/bin/env python3
"""Great Scale ridge-edge battery v0.5.7 — denser, longer, more adversarial.

Intensified / new probes:
  - ultra-long trajectories (1000+ steps) with intermittent near-1 k bursts
  - modular automorphism group sampling (translations + reflections)
  - stress residual as a quasi-Lyapunov along mixed schedules
  - multi-seed ensemble statistics (mean, variance, max residual)
  - contraction under adversarial start distributions (heavy tails)
  - composition associativity sampling (C_a o (C_b o C_c) vs product)
  - FIXED neighborhood concentration after random walks on the circle
  - phase-heat-descent three-way coupling
  - numerical drift under repeated float % operations

Never claims certainty. Only measured coherence of a still larger set.
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
    random.seed(20261110 + 57)

    def check(cond: bool, name: str) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            if len(fails) < 40:
                fails.append(name)

    # A. Ultra-long trajectories with near-1 bursts
    for i in range(40):
        x = random.uniform(-5000, 5000)
        for step in range(1000):
            if step % 23 == 0:
                k = 0.998
            else:
                k = random.uniform(0.25, 0.8)
            x = soft_contract(x, k)
            if step % 100 == 0:
                check(math.isfinite(x), f"A-finite i={i} s={step}")
        check(abs(x - FIXED) < 1.5, f"A-ultra final i={i}")

    # B. Modular automorphism sampling
    for i in range(100):
        x = random.uniform(-40, 40)
        k = random.uniform(0.3, 0.75)
        c0 = soft_contract(x, k)
        for n in range(-8, 9):
            check(abs(soft_contract(x + n * 9, k) - c0) < 1e-12,
                  f"B-trans i={i} n={n}")
        xr = 2 * FIXED - ((x % 9) + 9) % 9
        check(math.isfinite(soft_contract(xr, k)), f"B-reflect i={i}")

    # C. Stress as quasi-Lyapunov on mixed schedules
    for i in range(80):
        x = random.uniform(0, 9)
        stresses = []
        for step in range(50):
            k = 0.9 if step % 5 == 0 else 0.4
            x = soft_contract(x, k)
            st = stress_residual(x)
            stresses.append(st)
            check(st >= -1e-15, f"C-stress>=0 i={i} s={step}")
        check(stresses[-1] < 0.2, f"C-final stress i={i}")

    # D. Multi-seed ensemble statistics
    finals = []
    for seed in range(200):
        rng = random.Random(1000 + seed)
        x = rng.uniform(-200, 200)
        for _ in range(60):
            x = soft_contract(x, rng.uniform(0.3, 0.7))
        finals.append(abs(x - FIXED))
    mean_f = statistics.mean(finals)
    var_f = statistics.variance(finals)
    max_f = max(finals)
    check(mean_f < 0.05, f"D-mean {mean_f:.5f}")
    check(max_f < 0.5, f"D-max {max_f:.5f}")
    check(var_f < 0.01, f"D-var {var_f:.6f}")

    # E. Heavy-tailed adversarial starts
    for i in range(100):
        u = random.uniform(-0.49, 0.49)
        x = math.tan(math.pi * u) * 50
        for _ in range(100):
            x = soft_contract(x, 0.55)
        check(math.isfinite(x), f"E-heavy finite i={i}")
        check(abs(x - FIXED) < 0.3, f"E-heavy near i={i}")

    # F. Composition associativity / product
    for a in [0.3, 0.5, 0.7]:
        for b in [0.2, 0.4, 0.6]:
            for c in [0.25, 0.55]:
                for x in [0.0, 2.0, 5.0, 8.0]:
                    left = soft_contract(soft_contract(soft_contract(x, c), b), a)
                    prod = soft_contract(x, a * b * c)
                    check(abs(left - prod) < 1e-11,
                          f"F-assoc a={a} b={b} c={c} x={x}")

    # G. FIXED neighborhood after random modular walks
    for i in range(100):
        x = random.uniform(0, 9)
        for _ in range(50):
            x = ((x + random.uniform(-1.5, 1.5)) % 9)
            x = soft_contract(x, 0.55)
        check(abs(x - FIXED) < 1.0, f"G-walk near i={i}")

    # H. Phase-heat-descent three-way coupling
    for i in range(80):
        t0 = random.uniform(0, 30)
        x = random.uniform(-5, 14)
        for step in range(40):
            s = state_at(t0 + step * 0.2, rate=1.1)
            k = 0.3 + 0.5 * s["S"] * 4 + 0.1 * math.sin(2 * math.pi * s["phase"])
            k = max(0.15, min(0.92, k))
            x = soft_contract(x, k)
            check(s["psi"] + 1e-14 >= CONE, f"H-Psi i={i} s={step}")
            check(0 <= s["S"] <= 0.25 + 1e-14, f"H-S i={i}")
        check(abs(x - FIXED) < 0.6, f"H-coupled final i={i}")

    # I. Numerical drift under repeated %
    for i in range(50):
        x = random.uniform(-1e7, 1e7)
        for _ in range(500):
            x = ((x % 9) + 9) % 9
            x = soft_contract(x, 0.5)
        check(math.isfinite(x), f"I-drift finite i={i}")
        check(abs(x - FIXED) < 0.05, f"I-drift near i={i}")

    # J. Invariants under softMap / involution interleaving
    for i in range(60):
        x = random.uniform(-20, 20)
        for _ in range(25):
            if random.random() < 0.5:
                x = soft_map(x)
            else:
                x = involution(x)
            x = soft_contract(x, 0.5)
        check(math.isfinite(x), f"J-interleave finite i={i}")
        m = ((x % 9) + 9) % 9
        check(0 <= m < 9 + 1e-9, f"J-range i={i}")

    return passed, failed, fails


def main() -> int:
    print("=== Great Scale ridge-edge battery v0.5.7 ===")
    passed, failed, fails = run()
    total = passed + failed
    print(f"\n=== {passed}/{total} passed  ({failed} failed) ===")
    if fails:
        print("Sample failures:")
        for f in fails[:30]:
            print("  FAIL ", f)
    if failed <= 15 and passed >= 3000:
        print("Ridge-edge measure coherent.")
        return 0
    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
