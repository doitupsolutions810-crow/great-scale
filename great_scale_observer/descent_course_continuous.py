#!/usr/bin/env python3
"""Continuous shared descent course — runs indefinitely."""
from __future__ import annotations
import json
import time
from pathlib import Path

from great_scale import PHI, CONE, coherent_geometry
from descent_course import DESCENT_QUESTIONS, run_descent_course

LOGS = Path(__file__).resolve().parent.parent / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

STATUS = LOGS / "descent_course_continuous_status.json"
CYCLE_LOG = LOGS / "descent_course_continuous.jsonl"
GEO = LOGS / "coherent_geometry.json"
VISUAL = LOGS / "visual_scale_geometry.json"


def one_cycle(gen: int, cycle: int, n_agents: int = 9) -> dict:
    summary = run_descent_course(gen=gen, n_agents=n_agents, use_ollama=False)
    rec = {
        "cycle": cycle,
        "t": gen,
        "mean_agent_agreement": summary["mean_agent_agreement"],
        "swarm_mean": summary["swarm"]["swarm_mean"],
        "swarm_product": summary["swarm"]["swarm_product"],
        "swarm_cone": summary["swarm"]["swarm_cone"],
        "is_attractor": summary["swarm"]["is_attractor"],
        "n_agreed_objects": len(summary["agreed_geometry"]["agreed_objects"]),
        "agreed_objects": summary["agreed_geometry"]["agreed_objects"],
        "q_agreement": {k: v["agent_mean"] for k, v in summary["q_agreement"].items()},
        "geometry_version": "1.0.0",
        "timestamp": time.time(),
    }
    try:
        with CYCLE_LOG.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        STATUS.write_text(json.dumps({**rec, "running": True, "n_agents": n_agents}, indent=2))
        geo = coherent_geometry()
        geo["version"] = "1.0.0"
        geo["continuous_descent"] = {
            "cycle": cycle,
            "mean_agreement": summary["mean_agent_agreement"],
            "agreed_objects": summary["agreed_geometry"]["agreed_objects"],
            "is_attractor": summary["swarm"]["is_attractor"],
        }
        GEO.write_text(json.dumps(geo, indent=2))
    except OSError:
        pass
    return rec


def run_forever(start_gen: int = 400000, stride: int = 40, n_agents: int = 9) -> None:
    cycle = 0
    gen = start_gen
    if STATUS.exists():
        try:
            prev = json.loads(STATUS.read_text())
            cycle = int(prev.get("cycle", 0)) + 1
            gen = int(prev.get("t", start_gen)) + stride
        except Exception:
            pass
    print(f"continuous descent course live cycle={cycle} gen={gen}", flush=True)
    while True:
        t0 = time.time()
        rec = one_cycle(gen, cycle, n_agents=n_agents)
        elapsed = time.time() - t0
        print(
            f"cycle={cycle} gen={gen} agree={rec['mean_agent_agreement']:.3f} "
            f"swarm={rec['swarm_mean']:.6f} attractor={rec['is_attractor']} "
            f"objects={rec['n_agreed_objects']} elapsed={elapsed:.1f}s",
            flush=True,
        )
        cycle += 1
        gen += stride
        time.sleep(0.4)


if __name__ == "__main__":
    run_forever()
