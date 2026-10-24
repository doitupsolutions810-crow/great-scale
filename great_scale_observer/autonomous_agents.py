"""Autonomous agents as dynamic fixed points."""
from __future__ import annotations
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List

from great_scale import PHI, PHI_INV, CONE, RESIDUAL_DIMS, state_at, ninefold_f, inward_fold

ROLE_BLOCKS = [4, 4, 4, 4, 3, 3, 3, 1, 1]


@dataclass
class FixedPoint:
    mean: float = PHI
    repeller: float = -PHI_INV
    cone: float = CONE
    block: int = 4
    stability: float = 1.0
    age: int = 0

    def product(self) -> float:
        return self.mean * self.repeller

    def lock_toward_law(self, strength: float = 0.15) -> None:
        self.mean += strength * (PHI - self.mean)
        self.repeller += strength * (-PHI_INV - self.repeller)
        self.cone = max(CONE, self.cone - strength * max(0.0, self.cone - CONE))
        if abs(self.mean) > 1e-9:
            self.repeller += strength * ((-1.0 / self.mean) - self.repeller)
        self.stability = min(1.0, self.stability + 0.02)

    def perturb(self, noise: float = 0.01) -> None:
        self.mean += random.uniform(-noise, noise)
        self.repeller += random.uniform(-noise, noise)
        self.cone = max(CONE, self.cone + random.uniform(-noise * 0.1, noise * 0.1))
        self.stability = max(0.0, self.stability - noise * 2)

    def score_state(self, psi: float) -> float:
        s = 0.0
        if abs(self.mean - PHI) < 0.08:
            s += 0.35
        if abs(self.product() + 1.0) < 0.15:
            s += 0.25
        if psi >= self.cone - 1e-9 and self.cone >= CONE - 1e-9:
            s += 0.25
        if self.block in RESIDUAL_DIMS:
            s += 0.15
        return s


@dataclass
class AutonomousAgent:
    id: int
    fp: FixedPoint = field(default_factory=FixedPoint)
    role: str = "Watch"
    hypotheses: List[str] = field(default_factory=list)
    last_claim: str = ""
    fate: str = "keep"

    def __post_init__(self) -> None:
        block = ROLE_BLOCKS[self.id % len(ROLE_BLOCKS)]
        self.fp.block = block
        self.role = {4: "Watch", 3: "Observer", 1: "Forward"}.get(block, "Watch")

    def autonomy_step(self, st: Dict[str, Any], peers: List["AutonomousAgent"]) -> Dict[str, Any]:
        self.fp.age += 1
        self.fp.perturb(noise=0.008 * (1.0 - self.fp.stability))
        sc = self.fp.score_state(st["psi"])
        if abs(self.fp.mean - PHI) > 0.12:
            sc *= 0.5

        kind = random.choice([
            "re_lock_mean", "hold_cone", "assert_block",
            "ninefold_pair", "plot_height", "radial_step", "exchange_pull",
        ])
        claim = ""
        if kind == "re_lock_mean":
            self.fp.lock_toward_law(0.25)
            claim = f"fp.mean→{self.fp.mean:.6f} (φ-lock)"
        elif kind == "hold_cone":
            self.fp.cone = max(CONE, self.fp.cone)
            claim = f"fp.cone={self.fp.cone:.6f} ≥ √5−2"
        elif kind == "assert_block":
            claim = f"fp.block={self.fp.block} role={self.role}"
        elif kind == "ninefold_pair":
            a = self.id % 9
            claim = f"involution ({a},{ninefold_f(a)}) f∘f=id"
        elif kind == "plot_height":
            claim = f"height H=S={st['S']:.4f} above fp.cone"
        elif kind == "radial_step":
            claim = f"λ={st['lambda']:.6f} from fp"
        else:
            peer = random.choice(peers)
            if peer.id != self.id and peer.fp.stability >= self.fp.stability:
                self.fp.mean += 0.1 * (peer.fp.mean - self.fp.mean)
                self.fp.cone = max(CONE, 0.5 * (self.fp.cone + peer.fp.cone))
                claim = f"pull←A{peer.id} mean={self.fp.mean:.5f}"
            else:
                self.fp.lock_toward_law(0.1)
                claim = "self-lock"

        if sc < 0.45:
            self.fate = "dissipate"
            self.hypotheses.clear()
            self.fp.mean = PHI + random.uniform(-0.02, 0.02)
            self.fp.repeller = -PHI_INV
            self.fp.cone = CONE
            self.fp.stability = 0.3
            claim = f"dissipate→rebirth block={self.fp.block}"
        else:
            self.fate = "keep"
            self.fp.lock_toward_law(0.08)
            self.hypotheses.append(claim)
            if len(self.hypotheses) > 8:
                self.hypotheses = self.hypotheses[-8:]

        self.last_claim = claim
        return {
            "t": st["generation"], "agent": self.id, "role": self.role,
            "kind": kind, "claim": claim, "fate": self.fate, "score": round(sc, 4),
            "fp": {
                "mean": round(self.fp.mean, 6), "repeller": round(self.fp.repeller, 6),
                "product": round(self.fp.product(), 6), "cone": round(self.fp.cone, 6),
                "block": self.fp.block, "stability": round(self.fp.stability, 4),
            },
            "phase": st["phase"], "S": st["S"], "psi": st["psi"],
        }


def swarm_fixed_point(agents: List[AutonomousAgent]) -> Dict[str, Any]:
    n = max(1, len(agents))
    mean = sum(a.fp.mean for a in agents) / n
    rep = sum(a.fp.repeller for a in agents) / n
    cone = sum(a.fp.cone for a in agents) / n
    stab = sum(a.fp.stability for a in agents) / n
    blocks = [a.fp.block for a in agents]
    return {
        "swarm_mean": round(mean, 6),
        "swarm_repeller": round(rep, 6),
        "swarm_product": round(mean * rep, 6),
        "swarm_cone": round(cone, 6),
        "swarm_stability": round(stab, 4),
        "blocks": blocks,
        "distance_to_phi": round(abs(mean - PHI), 6),
        "is_attractor": abs(mean - PHI) < 0.05 and abs(mean * rep + 1.0) < 0.1,
    }
