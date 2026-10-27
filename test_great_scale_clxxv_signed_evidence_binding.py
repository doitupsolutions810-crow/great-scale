#!/usr/bin/env python3
"""CLXXV: acceptance needs a digest-bound, source-signed fresh payload and separate E/G gates."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

CONTRACT = {
    "version": "5.4.0",
    "runtime": "read-only-dynamic",
    "privacy": "local-only",
    "serverSideEvidenceStorage": False,
    "syntheticEvidenceRejected": True,
    "productionEvidenceClassRequired": True,
    "requiredEvidenceClass": "production-acceptance",
    "requiredEnvironment": "production",
    "mandatoryGates": 7,
}
SOURCE_IDENTITY = "control12-evidence-console"
CHECK_IDS = [f"E{i}" for i in range(7)]
SOURCE_FIELDS = [
    "sourceIdentity", "sourceKeyId", "sourceEvidenceDigest", "sourceSignature",
    "sourceGeneratedAt", "sourceExpiresAt",
]
MAX_AGE = timedelta(minutes=5)
MAX_FUTURE_SKEW = timedelta(seconds=30)
DIGEST_RE = re.compile(r"^[a-f0-9]{64}$")
SIGNATURE_RE = re.compile(r"^[A-Za-z0-9+/]{86}==$")


def canonical_json(value):
    """Sorted compact JSON matching the producer/Node consumer canonicalization."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_status(status):
    unsigned = dict(status)
    unsigned.pop("sourceEvidenceDigest", None)
    unsigned.pop("sourceSignature", None)
    return hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()


def parse_timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        text = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def make_schema(key_id):
    props = {key: {"const": value} for key, value in CONTRACT.items()}
    props.update({
        "sourceIdentity": {"const": SOURCE_IDENTITY},
        "sourceKeyId": {"const": key_id},
        "sourceEvidenceDigest": {"type": "string", "pattern": r"^[a-f0-9]{64}$"},
        "sourceSignature": {"type": "string", "pattern": r"^[A-Za-z0-9+/]{86}==$"},
        "sourceGeneratedAt": {"type": "string", "format": "date-time"},
        "sourceExpiresAt": {"type": "string", "format": "date-time"},
        "overall": {"const": "READY"},
        "gates": {
            "type": "array", "minItems": 7, "maxItems": 7, "uniqueItems": True,
            "allOf": [
                {"contains": {"type": "object", "required": ["id"], "properties": {"id": {"const": gate_id}}},
                 "minContains": 1, "maxContains": 1}
                for gate_id in CHECK_IDS
            ],
            "items": {"type": "object", "additionalProperties": False, "required": ["id", "status"],
                      "properties": {"id": {"enum": CHECK_IDS}, "status": {"const": "READY"}}},
        },
    })
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object", "additionalProperties": False,
        "required": [*CONTRACT, *SOURCE_FIELDS, "overall", "gates"],
        "properties": props,
    }


def make_status(now, key_id="fixture-key-1"):
    status = {
        **CONTRACT,
        "sourceIdentity": SOURCE_IDENTITY,
        "sourceKeyId": key_id,
        "sourceGeneratedAt": now.isoformat().replace("+00:00", "Z"),
        "sourceExpiresAt": (now + timedelta(seconds=60)).isoformat().replace("+00:00", "Z"),
        "overall": "READY",
        "gates": [{"id": gate_id, "status": "READY"} for gate_id in CHECK_IDS],
    }
    status["sourceEvidenceDigest"] = digest_status(status)
    # The model receives crypto verification as an independent observation.
    # The production Node producer tests exercise actual Ed25519 signing/verification.
    status["sourceSignature"] = "A" * 86 + "=="
    return status


def accept(status, schema, *, expected_key_id, signature_valid, now):
    failures = set()
    if not isinstance(status, dict):
        return False, {"status-not-object"}
    for key, expected in CONTRACT.items():
        if status.get(key) != expected:
            failures.add("contract:" + key)
    if status.get("overall") != "READY":
        failures.add("overall")
    if status.get("sourceIdentity") != SOURCE_IDENTITY:
        failures.add("source-identity")
    if not expected_key_id or status.get("sourceKeyId") != expected_key_id:
        failures.add("source-key-pin")

    generated = parse_timestamp(status.get("sourceGeneratedAt"))
    expires = parse_timestamp(status.get("sourceExpiresAt"))
    if generated is None or expires is None:
        failures.add("timestamps-invalid")
    else:
        now = now.astimezone(timezone.utc)
        if generated > now + MAX_FUTURE_SKEW:
            failures.add("generated-future")
        if now - generated > MAX_AGE:
            failures.add("stale")
        if expires <= now:
            failures.add("expired")
        if expires <= generated or expires - generated > MAX_AGE:
            failures.add("lifetime-invalid")

    digest = status.get("sourceEvidenceDigest")
    if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest) or digest != digest_status(status):
        failures.add("digest-invalid")
    signature = status.get("sourceSignature")
    if not isinstance(signature, str) or not SIGNATURE_RE.fullmatch(signature) or not signature_valid:
        failures.add("signature-invalid")

    gates = status.get("gates")
    if not isinstance(gates, list) or len(gates) != 7:
        failures.add("checks-shape")
    else:
        ids = [entry.get("id") if isinstance(entry, dict) else None for entry in gates]
        if len(set(ids)) != 7 or set(ids) != set(CHECK_IDS):
            failures.add("checks-namespace-or-completeness")
        if any(not isinstance(entry, dict) or entry.get("status") != "READY" for entry in gates):
            failures.add("checks-not-ready")

    if not isinstance(schema, dict) or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        failures.add("schema-root")
    else:
        props = schema.get("properties", {})
        required = schema.get("required", [])
        required_fields = [*CONTRACT, *SOURCE_FIELDS, "overall", "gates"]
        if not all(key in required for key in required_fields):
            failures.add("schema-required-fields")
        for key, expected in CONTRACT.items():
            if props.get(key, {}).get("const") != expected:
                failures.add("schema-contract:" + key)
        if props.get("sourceIdentity", {}).get("const") != SOURCE_IDENTITY:
            failures.add("schema-source-identity")
        if props.get("sourceKeyId", {}).get("const") != expected_key_id or not expected_key_id:
            failures.add("schema-source-key-pin")
        if props.get("sourceEvidenceDigest", {}).get("pattern") != r"^[a-f0-9]{64}$":
            failures.add("schema-digest")
        if props.get("sourceSignature", {}).get("pattern") != r"^[A-Za-z0-9+/]{86}==$":
            failures.add("schema-signature")
        for field in ("sourceGeneratedAt", "sourceExpiresAt"):
            if props.get(field, {}).get("format") != "date-time":
                failures.add("schema-timestamp:" + field)
        gate_schema = props.get("gates", {})
        item_props = gate_schema.get("items", {}).get("properties", {})
        all_of = gate_schema.get("allOf", [])
        if (gate_schema.get("type") != "array" or gate_schema.get("minItems") != 7 or
                gate_schema.get("maxItems") != 7 or gate_schema.get("uniqueItems") is not True or
                item_props.get("id", {}).get("enum") != CHECK_IDS or
                item_props.get("status", {}).get("const") != "READY" or len(all_of) != 7 or
                {rule.get("contains", {}).get("properties", {}).get("id", {}).get("const") for rule in all_of} != set(CHECK_IDS) or
                any(rule.get("minContains") != 1 or rule.get("maxContains") != 1 for rule in all_of)):
            failures.add("schema-check-gates")

    return not failures, failures


def test_fresh_signed_envelope_and_schema_are_accepted():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now)
    accepted, failures = accept(status, make_schema("fixture-key-1"), expected_key_id="fixture-key-1",
                               signature_valid=True, now=now)
    assert accepted, failures


def test_mutated_status_cannot_reuse_old_digest_even_if_signature_checker_says_true():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now)
    status["privacy"] = "remote-storage"
    accepted, failures = accept(status, make_schema("fixture-key-1"), expected_key_id="fixture-key-1",
                               signature_valid=True, now=now)
    assert not accepted
    assert "digest-invalid" in failures


def test_stale_or_expired_source_claim_is_rejected_even_when_signature_is_valid():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now - timedelta(minutes=6))
    accepted, failures = accept(status, make_schema("fixture-key-1"), expected_key_id="fixture-key-1",
                               signature_valid=True, now=now)
    assert not accepted
    assert {"stale", "expired"} <= failures


def test_missing_or_different_public_key_pin_is_rejected():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now)
    accepted, failures = accept(status, make_schema("fixture-key-1"), expected_key_id=None,
                               signature_valid=True, now=now)
    assert not accepted
    assert "source-key-pin" in failures
    assert "schema-source-key-pin" in failures


def test_schema_cannot_omit_or_weaken_source_signature():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now)
    schema = make_schema("fixture-key-1")
    schema["required"].remove("sourceSignature")
    schema["properties"]["sourceSignature"] = {"type": "string"}
    accepted, failures = accept(status, schema, expected_key_id="fixture-key-1",
                               signature_valid=True, now=now)
    assert not accepted
    assert "schema-required-fields" in failures
    assert "schema-signature" in failures


def test_production_G_gates_cannot_be_replaced_by_console_E_checks_or_vice_versa():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now)
    status["gates"][-1]["id"] = "G6"
    status["sourceEvidenceDigest"] = digest_status(status)
    accepted, failures = accept(status, make_schema("fixture-key-1"), expected_key_id="fixture-key-1",
                               signature_valid=True, now=now)
    assert not accepted
    assert "checks-namespace-or-completeness" in failures


def test_client_probe_time_does_not_refresh_source_generated_time():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now - timedelta(minutes=6))
    status["checkedAt"] = now.isoformat().replace("+00:00", "Z")
    status["sourceEvidenceDigest"] = digest_status(status)
    accepted, failures = accept(status, make_schema("fixture-key-1"), expected_key_id="fixture-key-1",
                               signature_valid=True, now=now)
    assert not accepted
    assert "stale" in failures


def test_bad_cryptographic_verification_never_accepts():
    now = datetime(2026, 10, 27, tzinfo=timezone.utc)
    status = make_status(now)
    accepted, failures = accept(status, make_schema("fixture-key-1"), expected_key_id="fixture-key-1",
                               signature_valid=False, now=now)
    assert not accepted
    assert "signature-invalid" in failures


if __name__ == "__main__":
    tests = [
        test_fresh_signed_envelope_and_schema_are_accepted,
        test_mutated_status_cannot_reuse_old_digest_even_if_signature_checker_says_true,
        test_stale_or_expired_source_claim_is_rejected_even_when_signature_is_valid,
        test_missing_or_different_public_key_pin_is_rejected,
        test_schema_cannot_omit_or_weaken_source_signature,
        test_production_G_gates_cannot_be_replaced_by_console_E_checks_or_vice_versa,
        test_client_probe_time_does_not_refresh_source_generated_time,
        test_bad_cryptographic_verification_never_accepts,
    ]
    for test_fn in tests:
        test_fn()
    print(f"PASS CLXXV signed evidence-binding model ({len(tests)}/{len(tests)} tests)")
