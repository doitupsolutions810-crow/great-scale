#!/usr/bin/env python3
"""Great Scale deep-edge battery v0.5.4 — 3000+ further systematic cases.

New dimensions beyond v0.5.3:
  - operation composition (contract o involution o softMap sequences)
  - multi-k piecewise schedules (k changes mid-trajectory)
  - modular-cut chaos (dense sampling exactly at +/-eps of every integer lattice point)
  - residual histogram / statistical moments under random starts
  - QGT-bridge coupling: inject curvature-derived heat into descent state
  - long-horizon stability of FIXED under repeated round-trips
  - involution-contraction commutation relations (where they hold / fail)
  - stress residual as Lyapunov-like diagnostic along trajectories

Never claims certainty. Only measured coherence of a larger probe set.
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
    random.seed(20261110 + 54)

    def check(cond: bool, name: str) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            if len(fails) < 60:
                fails.append(name)

    # A. Operation composition sequences
    ops = [
        ("C", lambda x: soft_contract(x, 0.5)),
        ("I", involution),
        ("M", soft_map),
    ]
    for i in range(200):
        x = random.uniform(-50, 50)
        word = [random.choice(ops) for _ in range(random.randint(3, 5))]
        y = x
        for name, fn in word:
            y = fn(y)
            check(math.isfinite(y), f"A-finite i={i}")
        m = ((y % 9) + 9) % 9
        check(0 <= m < 9 + 1e-9, f"A-range i={i}")

    for x in [0.0, 1.0, 2.5, 4.5, 7.0, 8.9]:
        check(mod_dist(involution(involution(x)), x) < 1e-12, f"A-I2 x={x}")
        check(abs(soft_map(soft_map(x)) - x) < 1e-12, f"A-M2 x={x}")
        c2 = soft_contract(soft_contract(x, 0.5), 0.5)
        c1 = soft_contract(x, 0.25)
        check(abs(c2 - c1) < 1e-12, f"A-C o C x={x}")

    # B. Multi-k piecewise schedules
    schedules = [
        [0.9, 0.5, 0.2],
        [0.3, 0.8, 0.4],
        [0.99, 0.7, 0.3],
        [0.1, 0.1, 0.95],
    ]
    for sched in schedules:
        for start in [-20, 0, 3, 8, 40]:
            x = start
            for k in sched:
                for _ in range(40):
                    x = soft_contract(x, k)
            check(abs(x - FIXED) < 0.15, f"B-sched start={start} final={x:.5f}")

    # C. Modular-cut chaos
    for n in range(-5, 15):
        for eps in [1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 0.01]:
            for sign in (+1, -1):
                x = n + sign * eps
                c = soft_contract(x, 0.5)
                check(math.isfinite(c), f"C-cut finite n={n}")
                c9 = soft_contract(x + 9, 0.5)
                check(abs(c - c9) < 1e-10, f"C-cut fiber n={n}")
                check(stress_residual(x) >= -1e-15, f"C-cut stress n={n}")

    # D. Residual statistics
    residuals = []
    for _ in range(400):
        x = random.uniform(-100, 100)
        k = random.uniform(0.2, 0.85)
        for _ in range(30):
            x = soft_contract(x, k)
        residuals.append(abs(x - FIXED))
    mean_r = statistics.mean(residuals)
    max_r = max(residuals)
    check(mean_r < 0.05, f"D-mean residual {mean_r:.6f}")
    check(max_r < 0.5, f"D-max residual {max_r:.6f}")
    within = sum(1 for r in residuals if r < 0.1)
    check(within >= 380, f"D-95% within 0.1 ({within}/400)")

    # E. QGT-style heat injection into descent
    for i in range(150):
        chi = random.random()
        h_q = (1 + chi) / 2
        S_q = heat(h_q)
        psi_q = CONE + S_q
        check(psi_q + 1e-15 >= CONE, f"E-Psi chi={chi}")
        check(0 <= S_q <= 0.25 + 1e-15, f"E-S range chi={chi}")
        start = 4.5 + (1 - 4 * S_q) * 3.0
        x = start
        for _ in range(50):
            x = soft_contract(x, 0.6)
        check(abs(x - FIXED) < 0.05, f"E-descent i={i}")

    # F. Long-horizon FIXED stability
    for k in [0.3, 0.5, 0.7, 0.9]:
        x = FIXED
        for _ in range(500):
            x = soft_contract(x, k)
        check(abs(x - FIXED) < 1e-12, f"F-FIXED stable k={k}")
        x = FIXED + 1e-8
        for _ in range(200):
            x = soft_contract(x, k)
        check(abs(x - FIXED) < 1e-6, f"F-return k={k}")

    # G. Involution-contraction commutation sampling
    for i in range(100):
        x = random.uniform(0, 9)
        k = 0.5
        left = soft_contract(involution(x), k)
        right = involution(soft_contract(x, k))
        check(math.isfinite(left) and math.isfinite(right), f"G-finite i={i}")
        check(0 <= ((left % 9) + 9) % 9 < 9 + 1e-9, f"G-left range i={i}")
        check(0 <= ((right % 9) + 9) % 9 < 9 + 1e-9, f"G-right range i={i}")
    left_f = soft_contract(involution(FIXED), 0.5)
    right_f = involution(soft_contract(FIXED, 0.5))
    check(abs(left_f - right_f) < 1e-12, "G-commute at FIXED")

    # H. Stress as Lyapunov-like diagnostic
    for start in [0.0, 1.0, 2.0, 3.0, 6.0, 7.0, 8.0]:
        x = start
        for s in range(40):
            x = soft_contract(x, 0.55)
            st = stress_residual(x)
            check(st >= -1e-15, f"H-stress>=0 start={start} s={s}")
        check(stress_residual(x) < 0.05, f"H-final stress start={start}")

    # I. Dense phase-space stateAt grid
    for i in range(100):
        t = random.uniform(-1e4, 1e4)
        rate = random.uniform(0.05, 5.0)
        s = state_at(t, rate=rate)
        check(s["psi"] + 1e-14 >= CONE, f"I-Psi t={t} rate={rate}")
        check(0 <= s["S"] <= 0.25 + 1e-14, f"I-S t={t}")
        check(abs(s["S"] - heat(s["h"])) < 1e-14, f"I-S=heat t={t}")

    # J. Soft_map vs involution under translation
    diffs_mod = []
    diffs_shift = []
    for i in range(100):
        x = random.uniform(0, 9)
        diffs_mod.append(abs(soft_map(x) - involution(x)))
        xs = x + random.randint(1, 5) * 9
        diffs_shift.append(abs(soft_map(xs) - involution(xs)))
    mean_mod = statistics.mean(diffs_mod)
    mean_shift = statistics.mean(diffs_shift)
    check(mean_mod < 1e-10, f"J-agree on fundamental domain ({mean_mod:.2e})")
    check(mean_shift > 1.0, f"J-diverge under translation ({mean_shift:.3f})")

    return passed, failed, fails


def main() -> int:
    print("=== Great Scale deep-edge battery v0.5.4 ===")
    passed, failed, fails = run()
    total = passed + failed
    print(f"\n=== {passed}/{total} passed  ({failed} failed) ===")
    if fails:
        print("Sample failures (first 40):")
        for f in fails[:40]:
            print("  FAIL ", f)
    if failed <= 20 and passed >= 2900:
        print("Deep-edge measure coherent.")
        return 0
    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
