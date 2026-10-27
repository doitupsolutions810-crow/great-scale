#!/usr/bin/env python3
"""CLXXXIX policy model: residual input must be finite and topology-domain bounded."""
import math
import re

DECIMAL_NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
MIN_RESIDUAL = 0.0
MAX_RESIDUAL = 0.25


def parse_residual(raw):
    if raw is None:
        value = 0.0
        source = "default"
    else:
        if not isinstance(raw, str) or not raw.strip():
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        normalized = raw.strip()
        if not DECIMAL_NUMBER.fullmatch(normalized):
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        try:
            value = float(normalized)
        except ValueError:
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        if not math.isfinite(value):
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        mantissa = re.split(r"[eE]", normalized, maxsplit=1)[0]
        if value == 0 and re.search(r"[1-9]", mantissa):
            return {"valid": False, "value": None, "decision": "HOLD_INVALID_RESIDUAL"}
        if value < MIN_RESIDUAL or value > MAX_RESIDUAL:
            return {"valid": False, "value": None, "decision": "HOLD_RESIDUAL_DOMAIN"}
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
    for raw in ("0", "0.125", "0.25", ".125", "1.25e-1"):
        result = parse_residual(raw)
        assert result["valid"] and result["decision"] is None, raw
    for raw in ("", "   ", "NaN", "Infinity", "-Infinity", "bad", "0x10", "0b10", "1e999", "1e-999"):
        result = parse_residual(raw)
        assert not result["valid"] and result["decision"] == "HOLD_INVALID_RESIDUAL", raw
    for raw in ("-0.0001", "-0.125", "0.2500001", "1", "1e100"):
        result = parse_residual(raw)
        assert not result["valid"] and result["decision"] == "HOLD_RESIDUAL_DOMAIN", raw
    assert parse_residual("0")["decision"] is None
    assert parse_residual("0.25")["decision"] is None
    print("CLXXXIX finite residual boundary model: PASS")
    print("finite/default values inside [0, 0.25]: PASS")
    print("malformed/non-finite/underflow values: HOLD_INVALID_RESIDUAL")
    print("finite out-of-domain values: HOLD_RESIDUAL_DOMAIN")
    print("scope: Great Scale policy model only; JavaScript integration/CI still requires verification")


if __name__ == "__main__":
    main()
