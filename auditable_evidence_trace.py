"""Hash-chained audit trace for predictable adaptive e-processes.

A bet record commits to the past-history digest and lambda before the outcome
record is appended. The hash chain detects later edits to serialized records;
it does not prove trusted timestamps, prevent an operator from rewriting the
entire chain, or prove a strategy had no hidden information.
"""
from __future__ import annotations
import hashlib, json, math
from collections.abc import Callable, Sequence

BetStrategy = Callable[[tuple[int, ...]], float]
GENESIS = "0" * 64

def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()

def build_auditable_trace(observations: Sequence[int], q0: float, strategy: BetStrategy) -> dict[str, object]:
    q0 = float(q0)
    if not math.isfinite(q0) or not 0 < q0 < 1:
        raise ValueError("q0 must be finite and strictly between 0 and 1")
    xs = list(observations)
    if any(isinstance(x, bool) or x not in (0, 1) for x in xs):
        raise ValueError("observations must contain only integer 0 or 1 values")
    history: tuple[int, ...] = ()
    wealth = 1.0
    previous_hash = GENESIS
    records = []
    for t, x in enumerate(xs, start=1):
        lam = float(strategy(history))
        if not math.isfinite(lam) or not 0 <= lam <= 1.0 / q0:
            raise ValueError("bet must be finite and in [0, 1/q0]")
        bet_payload = {"kind": "bet", "step": t, "previous_hash": previous_hash,
                       "history_digest": _digest(list(history)), "lambda": lam, "q0": q0}
        bet_hash = _digest(bet_payload)
        bet_record = {**bet_payload, "record_hash": bet_hash}
        outcome_payload = {"kind": "outcome", "step": t, "previous_hash": bet_hash, "outcome": x}
        outcome_hash = _digest(outcome_payload)
        wealth *= 1.0 + lam * (x - q0)
        records.extend([{**bet_record}, {**outcome_payload, "record_hash": outcome_hash, "wealth": wealth}])
        previous_hash = outcome_hash
        history += (x,)
    return {"schema": "great-scale-audit-trace-v1", "q0": q0, "genesis": GENESIS,
            "records": records, "final_hash": previous_hash}

def verify_auditable_trace(trace: dict[str, object]) -> dict[str, object]:
    try:
        q0 = float(trace["q0"])
        if not math.isfinite(q0) or not 0 < q0 < 1 or trace.get("genesis") != GENESIS:
            return {"valid": False, "reason": "invalid header"}
        records = trace["records"]
        if not isinstance(records, list) or len(records) % 2:
            return {"valid": False, "reason": "records must be bet/outcome pairs"}
        history: tuple[int, ...] = ()
        wealth = 1.0
        previous_hash = GENESIS
        for i in range(0, len(records), 2):
            bet, outcome = records[i], records[i + 1]
            if bet.get("kind") != "bet" or outcome.get("kind") != "outcome":
                return {"valid": False, "reason": "incorrect record order"}
            bp = {k: bet[k] for k in ("kind", "step", "previous_hash", "history_digest", "lambda", "q0")}
            if bet.get("record_hash") != _digest(bp) or bet["previous_hash"] != previous_hash:
                return {"valid": False, "reason": "bet hash or chain mismatch"}
            if bet["step"] != i // 2 + 1 or bet["q0"] != q0 or bet["history_digest"] != _digest(list(history)):
                return {"valid": False, "reason": "bet context mismatch"}
            lam = float(bet["lambda"])
            if not math.isfinite(lam) or not 0 <= lam <= 1 / q0:
                return {"valid": False, "reason": "invalid betting fraction"}
            op = {k: outcome[k] for k in ("kind", "step", "previous_hash", "outcome")}
            if outcome.get("record_hash") != _digest(op) or outcome["previous_hash"] != bet["record_hash"]:
                return {"valid": False, "reason": "outcome hash or chain mismatch"}
            x = outcome["outcome"]
            if isinstance(x, bool) or x not in (0, 1) or outcome["step"] != bet["step"]:
                return {"valid": False, "reason": "invalid outcome record"}
            wealth *= 1 + lam * (x - q0)
            if not math.isclose(float(outcome.get("wealth", float("nan"))), wealth, rel_tol=1e-12, abs_tol=1e-12):
                return {"valid": False, "reason": "wealth mismatch"}
            history += (x,)
            previous_hash = outcome["record_hash"]
        if trace.get("final_hash") != previous_hash:
            return {"valid": False, "reason": "final hash mismatch"}
        return {"valid": True, "records_verified": len(records), "observations_verified": len(history), "final_wealth": wealth, "final_hash": previous_hash}
    except (KeyError, TypeError, ValueError, OverflowError):
        return {"valid": False, "reason": "malformed trace"}
