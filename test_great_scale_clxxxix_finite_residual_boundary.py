#!/usr/bin/env python3
"""CLXXXIX policy model: malformed residual inputs must never satisfy the cone gate."""
import math


def parse_residual(raw):
    if raw is None:
        value = 0.0
        source = "default"
    else:
        if not isinstance(raw, str) or not raw.strip():
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        try:
            value = float(raw)
        except ValueError:
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        if not math.isfinite(value):
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        source = "environment"

    phi = (1 + math.sqrt(5)) / 2
    cone = (phi - 1) ** 2
    cone_ok = cone + value >= cone - 1e-12
    decision = None if cone_ok else "HOLD_RESIDUAL_CONE"
    return {
        "valid": True,
        "value": value,
        "source": source,
        "cone_compliant": cone_ok,
        "decision": decision,
    }


def main():
    default = parse_residual(None)
    assert default["valid"] and default["value"] == 0 and default["decision"] is None
    for raw in ("0", "0.125", "1e-3"):
        result = parse_residual(raw)
        assert result["valid"] and result["decision"] is None, raw
    for raw in ("", "   ", "NaN", "Infinity", "-Infinity", "bad", "1e999"):
        result = parse_residual(raw)
        assert not result["valid"] and result["decision"] == "HOLD_INVALID_RESIDUAL", raw
    negative = parse_residual("-0.125")
    assert negative["valid"] and not negative["cone_compliant"]
    assert negative["decision"] == "HOLD_RESIDUAL_CONE"
    print("CLXXXIX finite residual boundary model: PASS")
    print("finite/default cases: PASS")
    print("malformed/non-finite cases: HOLD_INVALID_RESIDUAL")
    print("finite cone violation: HOLD_RESIDUAL_CONE")
    print("scope: Great Scale policy model only; JavaScript integration/CI still requires verification")


if __name__ == "__main__":
    main()
