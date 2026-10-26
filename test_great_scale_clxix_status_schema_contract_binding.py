#!/usr/bin/env python3
"""CLXIX: HTTP reachability and cross-document claims do not establish trust."""

EXPECTED = {
    "version": "5.3.1",
    "runtime": "static",
    "privacy": "local-only",
    "mandatoryGates": 7,
    "serverSideEvidenceStorage": False,
    "syntheticEvidenceRejected": True,
    "productionEvidenceClassRequired": True,
    "requiredEvidenceClass": "production-acceptance",
    "requiredEnvironment": "production",
}
GATE_IDS = tuple(f"G{i}" for i in range(7))
SCHEMA_URI = "https://json-schema.org/draft/2020-12/schema"


def good_status():
    return {
        **EXPECTED,
        "overall": "READY",
        "gates": {gate: "READY" for gate in GATE_IDS},
    }


def allow(value):
    return {"const": value}


def good_schema():
    return {
        "$schema": SCHEMA_URI,
        "type": "object",
        "required": [*EXPECTED.keys(), "overall", "gates"],
        "properties": {
            **{key: allow(value) for key, value in EXPECTED.items()},
            "overall": {"enum": ["READY", "HOLD"]},
            "gates": {
                "type": "object",
                "required": list(GATE_IDS),
                "properties": {gate: allow("READY") for gate in GATE_IDS},
            },
        },
    }


def property_allows(schema_property, expected):
    if not isinstance(schema_property, dict):
        return False
    if "const" in schema_property:
        return schema_property["const"] == expected
    enum = schema_property.get("enum")
    return isinstance(enum, list) and expected in enum


def validate_status_schema(status, schema, url="https://evidence.example.invalid/api/status"):
    failures = []
    if not isinstance(url, str) or not url.startswith("https://"):
        failures.append("public_endpoint_not_https")
    if not isinstance(status, dict):
        return False, ["status_document_not_object", *failures]
    if not isinstance(schema, dict):
        return False, ["schema_document_not_object", *failures]

    for key, expected in EXPECTED.items():
        if status.get(key) != expected:
            failures.append(f"status.{key}")
    if status.get("overall") != "READY":
        failures.append("status.overall")

    gates = status.get("gates")
    if isinstance(gates, dict):
        valid_status_gates = (
            set(gates) == set(GATE_IDS)
            and all(gates.get(gate) == "READY" for gate in GATE_IDS)
        )
    elif isinstance(gates, list):
        gate_entries = [item for item in gates if isinstance(item, dict)]
        ids = [item.get("id") for item in gate_entries]
        valid_status_gates = (
            len(gates) == len(GATE_IDS)
            and len(gate_entries) == len(GATE_IDS)
            and set(ids) == set(GATE_IDS)
            and len(set(ids)) == len(GATE_IDS)
            and all(item.get("status") == "READY" for item in gate_entries)
        )
    else:
        valid_status_gates = False
    if not valid_status_gates:
        failures.append("status.gates")

    if schema.get("$schema") != SCHEMA_URI:
        failures.append("schema.$schema")
    if schema.get("type") != "object":
        failures.append("schema.type")
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        failures.append("schema.properties")
    else:
        for key, expected in EXPECTED.items():
            if not property_allows(properties.get(key), expected):
                failures.append(f"schema.properties.{key}")
        if not property_allows(properties.get("overall"), "READY"):
            failures.append("schema.properties.overall")
        gate_schema = properties.get("gates")
        gate_properties = gate_schema.get("properties") if isinstance(gate_schema, dict) else None
        if gate_schema and gate_schema.get("type") == "object":
            gate_required = gate_schema.get("required")
            object_gate_schema_valid = (
                isinstance(gate_properties, dict)
                and set(gate_properties) == set(GATE_IDS)
                and isinstance(gate_required, list)
                and set(gate_required) == set(GATE_IDS)
                and len(gate_required) == len(GATE_IDS)
                and all(property_allows(gate_properties.get(gate), "READY") for gate in GATE_IDS)
            )
            array_gate_schema_valid = False
        elif gate_schema and gate_schema.get("type") == "array":
            item_schema = gate_schema.get("items")
            item_properties = item_schema.get("properties") if isinstance(item_schema, dict) else None
            item_required = item_schema.get("required") if isinstance(item_schema, dict) else None
            id_enum = item_properties.get("id", {}).get("enum") if isinstance(item_properties, dict) and isinstance(item_properties.get("id"), dict) else None
            rules = gate_schema.get("allOf")
            exact_occurrence_rules = (
                isinstance(rules, list)
                and len(rules) == len(GATE_IDS)
                and all(any(
                    isinstance(rule, dict)
                    and isinstance(rule.get("contains"), dict)
                    and rule["contains"].get("properties", {}).get("id", {}).get("const") == gate
                    and "id" in rule["contains"].get("required", [])
                    and rule.get("minContains") == 1
                    and rule.get("maxContains") == 1
                    for rule in rules
                ) for gate in GATE_IDS)
            )
            array_gate_schema_valid = (
                gate_schema.get("minItems") == len(GATE_IDS)
                and gate_schema.get("maxItems") == len(GATE_IDS)
                and gate_schema.get("uniqueItems") is True
                and isinstance(item_schema, dict)
                and item_schema.get("type") == "object"
                and isinstance(item_required, list)
                and "id" in item_required and "status" in item_required
                and isinstance(id_enum, list)
                and len(id_enum) == len(GATE_IDS)
                and set(id_enum) == set(GATE_IDS)
                and property_allows(item_properties.get("status"), "READY")
                and exact_occurrence_rules
            )
            object_gate_schema_valid = False
        else:
            object_gate_schema_valid = False
            array_gate_schema_valid = False
        if not object_gate_schema_valid and not array_gate_schema_valid:
            failures.append("schema.properties.gates")

    required = schema.get("required")
    if not isinstance(required, list):
        failures.append("schema.required")
    else:
        for key in [*EXPECTED.keys(), "overall", "gates"]:
            if key not in required:
                failures.append(f"schema.required.{key}")

    return not failures, failures


def procurement_authorized(core_ready, public_contract_verified, local_fallback_observed, local_opt_in, force=False):
    # Force is intentionally absent from the authority rule.
    return core_ready and (
        public_contract_verified or (local_fallback_observed and local_opt_in)
    )


def test_valid_independent_status_and_schema_contract_passes():
    valid, failures = validate_status_schema(good_status(), good_schema())
    assert valid, failures


def test_schema_cannot_supply_a_missing_live_status_claim():
    status = good_status()
    del status["syntheticEvidenceRejected"]
    valid, failures = validate_status_schema(status, good_schema())
    assert not valid
    assert "status.syntheticEvidenceRejected" in failures


def test_live_status_cannot_compensate_for_a_weakened_schema():
    schema = good_schema()
    schema["properties"]["syntheticEvidenceRejected"] = {"type": "boolean"}
    valid, failures = validate_status_schema(good_status(), schema)
    assert not valid
    assert "schema.properties.syntheticEvidenceRejected" in failures


def test_http_200_without_contract_is_not_trust():
    valid, failures = validate_status_schema({"ok": True}, {"ok": True})
    assert not valid
    assert "status.version" in failures
    assert "schema.$schema" in failures


def test_gate_hold_blocks_the_pair():
    status = good_status()
    status["gates"]["G6"] = "HOLD"
    valid, failures = validate_status_schema(status, good_schema())
    assert not valid
    assert "status.gates" in failures


def test_public_http_endpoint_is_not_accepted_as_trusted_public_evidence():
    valid, failures = validate_status_schema(good_status(), good_schema(), "http://evidence.example.invalid/api/status")
    assert not valid
    assert "public_endpoint_not_https" in failures


def test_force_cannot_change_authorization():
    args = dict(
        core_ready=True,
        public_contract_verified=False,
        local_fallback_observed=False,
        local_opt_in=False,
    )
    assert procurement_authorized(**args, force=False) is False
    assert procurement_authorized(**args, force=True) is False


def test_explicit_local_opt_in_is_only_the_degraded_fallback_path():
    assert procurement_authorized(True, False, True, True, force=False) is True
    assert procurement_authorized(True, False, False, True, force=True) is False




def array_status():
    return {**EXPECTED, "overall": "READY", "gates": [{"id": gate, "status": "READY"} for gate in GATE_IDS]}


def array_schema():
    schema = good_schema()
    schema["properties"]["gates"] = {
        "type": "array", "minItems": 7, "maxItems": 7, "uniqueItems": True,
        "allOf": [
            {"contains": {"type": "object", "required": ["id"], "properties": {"id": {"const": gate}}}, "minContains": 1, "maxContains": 1}
            for gate in GATE_IDS
        ],
        "items": {"type": "object", "required": ["id", "status"], "properties": {"id": {"enum": list(GATE_IDS)}, "status": allow("READY")}},
    }
    return schema


def test_array_gate_schema_requires_one_of_each_g0_g6():
    valid, failures = validate_status_schema(array_status(), array_schema())
    assert valid, failures


def test_array_schema_missing_exactly_once_gate_rule_fails_closed():
    schema = array_schema()
    schema["properties"]["gates"]["allOf"] = schema["properties"]["gates"]["allOf"][:-1]
    valid, failures = validate_status_schema(array_status(), schema)
    assert not valid
    assert "schema.properties.gates" in failures

def test_schema_must_require_all_seven_gate_keys():
    schema = good_schema()
    schema["properties"]["gates"]["required"] = list(GATE_IDS[:-1])
    valid, failures = validate_status_schema(good_status(), schema)
    assert not valid
    assert "schema.properties.gates" in failures


def test_unknown_gate_set_does_not_pass():
    status = good_status()
    status["gates"] = {**status["gates"], "G7": status["gates"].pop("G6")}
    valid, failures = validate_status_schema(status, good_schema())
    assert not valid
    assert "status.gates" in failures

if __name__ == "__main__":
    tests = [
        test_valid_independent_status_and_schema_contract_passes,
        test_schema_cannot_supply_a_missing_live_status_claim,
        test_live_status_cannot_compensate_for_a_weakened_schema,
        test_http_200_without_contract_is_not_trust,
        test_gate_hold_blocks_the_pair,
        test_public_http_endpoint_is_not_accepted_as_trusted_public_evidence,
        test_force_cannot_change_authorization,
        test_explicit_local_opt_in_is_only_the_degraded_fallback_path,
        test_schema_must_require_all_seven_gate_keys,
        test_unknown_gate_set_does_not_pass,
        test_array_gate_schema_requires_one_of_each_g0_g6,
        test_array_schema_missing_exactly_once_gate_rule_fails_closed,
    ]
    for test_fn in tests:
        test_fn()
    print(f"PASS CLXIX status/schema authority boundary ({len(tests)}/{len(tests)} tests)")
