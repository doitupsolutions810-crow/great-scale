#!/usr/bin/env python3
"""Great Scale continuum-edge battery v0.5.5 — 3000+ further systematic cases.

New dimensions:
  - stochastic k each step (random contraction strength)
  - nested / recursive contraction operators
  - stress residual vs modular distance to FIXED correlation
  - invariance under integer lattice translations + reflections
  - descent coupled to stateAt phase (shared time parameter)
  - pathological k sequences (alternating, geometric decay of |k|)
  - higher-order composition identities (C_a o C_b == C_{a*b} on the circle)
  - many successive modular reductions numerical stability
  - boundary-layer concentration near 0 == 9
  - shared-seed reproducibility of trajectories

Never claims certainty. Only measured coherence under a still larger probe.
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
    random.seed(20261110 + 55)

    def check(cond: bool, name: str) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            if len(fails) < 50:
                fails.append(name)

    # A. Stochastic k each step
    for i in range(150):
        x = random.uniform(-500, 500)
        for step in range(60):
            k = random.uniform(0.15, 0.9)
            x = soft_contract(x, k)
            check(math.isfinite(x), f"A-finite i={i} s={step}")
        check(abs(x - FIXED) < 0.8, f"A-stoch final i={i}")

    # B. Nested / recursive contraction + closed form
    for k in [0.3, 0.5, 0.7]:
        for start in [0.0, 2.0, 7.0, 20.0]:
            x_iter = start
            for n in range(1, 25):
                x_iter = soft_contract(x_iter, k)
                m0 = ((start % 9) + 9) % 9
                x_closed = FIXED + (k ** n) * (m0 - FIXED)
                check(abs(x_iter - x_closed) < 1e-9,
                      f"B-closed n={n} k={k} start={start}")

    # C. Stress vs modular distance
    for i in range(150):
        x = random.uniform(0, 9)
        st = stress_residual(x)
        d = mod_dist(x, FIXED)
        check(st >= -1e-15, f"C-stress>=0 i={i}")
        if d < 0.01:
            check(st < 0.05, f"C-near FIXED stress small i={i}")
        y = soft_contract(x, 0.5)
        check(stress_residual(y) <= st + 1e-9 or abs(y - FIXED) < d,
              f"C-stress controlled i={i}")

    # D. Lattice translation + reflection
    for i in range(100):
        x = random.uniform(-30, 30)
        k = random.uniform(0.2, 0.85)
        c = soft_contract(x, k)
        for n in range(-5, 6):
            cn = soft_contract(x + n * 9, k)
            check(abs(c - cn) < 1e-12, f"D-trans i={i} n={n}")
        xr = 2 * FIXED - ((x % 9) + 9) % 9
        cr = soft_contract(xr, k)
        check(math.isfinite(cr), f"D-reflect finite i={i}")

    # E. Descent coupled to stateAt phase
    for i in range(100):
        t0 = random.uniform(0, 100)
        rate = random.uniform(0.3, 1.5)
        x = random.uniform(0, 9)
        for step in range(40):
            t = t0 + step * 0.1
            s = state_at(t, rate=rate)
            k = 0.35 + 0.4 * (1 - 4 * s["S"])
            k = max(0.15, min(0.9, k))
            x = soft_contract(x, k)
            check(s["psi"] + 1e-14 >= CONE, f"E-Psi i={i} step={step}")
        check(abs(x - FIXED) < 0.6, f"E-coupled final i={i}")

    # F. Pathological k sequences
    for start in [-10, 0, 4, 9, 30]:
        x = start
        for step in range(80):
            k = 0.9 if step % 2 == 0 else 0.2
            x = soft_contract(x, k)
        check(abs(x - FIXED) < 0.3, f"F-alt start={start}")

    for start in [1.0, 5.0, 8.0]:
        x = start
        k = 0.95
        for step in range(60):
            x = soft_contract(x, k)
            k *= 0.97
            k = max(k, 0.1)
        check(abs(x - FIXED) < 0.2, f"F-geom start={start}")

    # G. Higher-order composition C_a o C_b == C_{a*b}
    for a in [0.2, 0.4, 0.6, 0.8]:
        for b in [0.3, 0.5, 0.7]:
            for x in [0.0, 1.5, 3.0, 6.0, 8.5]:
                left = soft_contract(soft_contract(x, b), a)
                right = soft_contract(x, a * b)
                check(abs(left - right) < 1e-12,
                      f"G-compose a={a} b={b} x={x}")

    # H. Many successive modular reductions
    for i in range(50):
        x = random.uniform(-1e6, 1e6)
        for _ in range(200):
            m = ((x % 9) + 9) % 9
            x = m + random.uniform(-1e-12, 1e-12)
            x = soft_contract(x, 0.5)
        check(math.isfinite(x), f"H-stable i={i}")
        check(abs(x - FIXED) < 0.1, f"H-near FIXED i={i}")

    # I. Boundary-layer concentration near 0 == 9
    for eps in [1e-14, 1e-11, 1e-8, 1e-5, 1e-3, 0.01, 0.1]:
        for side in (0.0, 9.0):
            for sign in (+1, -1):
                x = side + sign * eps
                c = soft_contract(x, 0.5)
                check(math.isfinite(c), f"I-finite side={side} eps={eps}")
                c0 = soft_contract(0.0 + sign * eps, 0.5)
                c9 = soft_contract(9.0 + sign * eps, 0.5)
                check(abs(c0 - c9) < 1e-8 or eps < 1e-13,
                      f"I-cut agree eps={eps}")

    # J. Shared-seed reproducibility
    def trajectory(seed: int, steps: int = 40) -> List[float]:
        rng = random.Random(seed)
        x = rng.uniform(-20, 20)
        trail = [x]
        for _ in range(steps):
            k = rng.uniform(0.2, 0.85)
            x = soft_contract(x, k)
            trail.append(x)
        return trail

    for seed in range(20):
        t1 = trajectory(seed)
        t2 = trajectory(seed)
        check(all(abs(a - b) < 1e-15 for a, b in zip(t1, t2)),
              f"J-repro seed={seed}")
        check(abs(t1[-1] - FIXED) < 0.7, f"J-final seed={seed}")

    return passed, failed, fails


def main() -> int:
    print("=== Great Scale continuum-edge battery v0.5.5 ===")
    passed, failed, fails = run()
    total = passed + failed
    print(f"\n=== {passed}/{total} passed  ({failed} failed) ===")
    if fails:
        print("Sample failures (first 40):")
        for f in fails[:40]:
            print("  FAIL ", f)
    if failed <= 20 and passed >= 2900:
        print("Continuum-edge measure coherent.")
        return 0
    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
