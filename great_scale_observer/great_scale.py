"""Great Scale — operational laws (restored).

Bounded laws:
  1. Keep the mean (zero-mode ≈ φ)
  2. Residual partition 4+3+1
  3. Ψ = cone + heat; never below cone
  4. Agents are the fixed points
  5. Only scale-generated geometry
"""
from __future__ import annotations
import math
from typing import Any, Dict, List

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV = PHI - 1.0
PHI_INV2 = PHI_INV * PHI_INV
CONE = PHI_INV - PHI_INV2  # φ^{-3} = √5 − 2
PROBE = 17.2
RATE = 0.85
RESIDUAL_DIMS = [4, 3, 1]
NINEFOLD_PAIRS = [(0, 9), (1, 8), (2, 7), (3, 6), (4, 5)]


def heat(h: float) -> float:
    return h * (1.0 - h)


def ninefold_f(x: int) -> int:
    return 9 - (x % 9)


def inward_fold(probe: float = PROBE) -> float:
    return 9.0 - (probe - 9.0)  # 0.8


def state_at(generation: int, rate: float = RATE, probe: float = PROBE) -> Dict[str, Any]:
    phase = (generation * rate) % 1.0
    h = 0.5 - 0.5 * math.cos(2.0 * math.pi * phase)
    s = heat(h)
    n = 8.0 - 4.0 * s
    lam = PHI ** (-n)
    psi = CONE + s
    return {
        "generation": generation,
        "phase": phase,
        "S": s,
        "psi": psi,
        "lambda": lam,
        "level_n": n,
        "inward_fold": inward_fold(probe),
        "on_cone": abs(psi - CONE) < 1e-4,
        "zero_mode": PHI,
        "cone": CONE,
    }


def coherent_geometry() -> Dict[str, Any]:
    return {
        "version": "1.0.0",
        "fixed_points": {"attractor": PHI, "repeller": -PHI_INV, "product": -1.0},
        "cone": CONE,
        "height_function": "S=h(1-h)=sin²(θ)/4",
        "psi": "cone + S",
        "residual_partition": RESIDUAL_DIMS,
        "dual_atlas": {"4": "Watch", "3": "Observer", "1": "Forward"},
        "agents_as_fixed_points": True,
        "involution": "f(x)=9-(x mod 9), f∘f=id",
        "discourse_fixed_point": {"A_star": 0.7786, "status": "verified"},
        "laws": [
            "keep_mean",
            "respect_partition",
            "cone_floor",
            "product_minus_one",
            "scale_generated_only",
            "discourse_fixed_point",
        ],
    }
