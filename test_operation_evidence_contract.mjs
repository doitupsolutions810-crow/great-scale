import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const schema = JSON.parse(readFileSync(new URL("./contracts/operation-evidence/v1.schema.json", import.meta.url), "utf8"));

const validEnvelope = () => ({
  schema_version: 1,
  operation_id: "op-01",
  request_digest: "a".repeat(64),
  parent_operation_id: null,
  parent_request_digest: null,
  event_id: "capability-authority:op-01:receipt",
  stage: "receipt",
  decision_state: "completed",
  producer: {
    repository: "example/service",
    commit_sha: "b".repeat(40),
  },
  observed_at: "2026-10-27T12:00:00.000Z",
  action: {
    type: "http",
    resource: "/records",
    method: "POST",
  },
  evidence_ref: "urn:example:evidence:123",
  authority_ref: "capability-123",
  attestation: {
    algorithm: "Ed25519",
    key_id: "executor-key-01",
    signature: "A".repeat(86) + "==",
  },
});

function matchesType(value, expected) {
  const types = Array.isArray(expected) ? expected : [expected];
  return types.some((type) => {
    if (type === "null") return value === null;
    if (type === "object") return value !== null && typeof value === "object" && !Array.isArray(value);
    if (type === "array") return Array.isArray(value);
    if (type === "integer") return Number.isInteger(value);
    if (type === "number") return typeof value === "number" && Number.isFinite(value);
    return typeof value === type;
  });
}

function validateAgainstSchema(value, rule = schema, path = "$") {
  const errors = [];
  const add = (reason) => errors.push(`${path}: ${reason}`);
  if (rule.type && !matchesType(value, rule.type)) return [`${path}: expected type ${JSON.stringify(rule.type)}`];
  if (Object.hasOwn(rule, "const") && value !== rule.const) add(`must equal ${JSON.stringify(rule.const)}`);
  if (rule.enum && !rule.enum.includes(value)) add(`must be one of ${rule.enum.join(", ")}`);

  if (rule === schema && value.stage === "receipt" && !Object.hasOwn(value, "attestation")) {
    add("receipt stage requires attestation metadata");
  }

  if (typeof value === "string") {
    if (rule.minLength !== undefined && value.length < rule.minLength) add("string is too short");
    if (rule.maxLength !== undefined && value.length > rule.maxLength) add("string is too long");
    if (rule.pattern && !(new RegExp(rule.pattern)).test(value)) add("string does not match required pattern");
    if (rule.format === "date-time") {
      const iso = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
      if (!iso.test(value) || Number.isNaN(Date.parse(value))) add("must be an ISO date-time");
    }
  }
  if (matchesType(value, "object")) {
    for (const key of rule.required || []) {
      if (!Object.hasOwn(value, key)) add(`missing required property ${key}`);
    }
    if (rule.additionalProperties === false) {
      for (const key of Object.keys(value)) {
        if (!Object.hasOwn(rule.properties || {}, key)) add(`unknown property ${key}`);
      }
    }
    for (const [key, childRule] of Object.entries(rule.properties || {})) {
      if (Object.hasOwn(value, key)) errors.push(...validateAgainstSchema(value[key], childRule, `${path}.${key}`));
    }
  }
  return errors;
}

function actionMatches(envelope, expected) {
  return JSON.stringify(envelope.action) === JSON.stringify({
    type: expected.type,
    resource: expected.resource,
    method: expected.method ?? null,
  });
}

test("v1 schema accepts a complete revision-bound operation receipt", () => {
  const candidate = validEnvelope();
  assert.deepEqual(validateAgainstSchema(candidate), []);
  assert.equal(schema.additionalProperties, false);
});

test("schema requires stable operation identity and per-service request digest", () => {
  const missingId = validEnvelope();
  delete missingId.operation_id;
  assert.ok(validateAgainstSchema(missingId).some((error) => error.includes("operation_id")));

  const badDigest = validEnvelope();
  badDigest.request_digest = "not-a-digest";
  assert.ok(validateAgainstSchema(badDigest).some((error) => error.includes("request_digest")));
});

test("parent operation linkage is explicit and validates its digest", () => {
  const child = validEnvelope();
  child.parent_operation_id = "root-operation";
  child.parent_request_digest = "c".repeat(64);
  assert.deepEqual(validateAgainstSchema(child), []);

  child.parent_request_digest = "broken";
  assert.ok(validateAgainstSchema(child).some((error) => error.includes("parent_request_digest")));
});

test("producer revision and observation time are required and typed", () => {
  const candidate = validEnvelope();
  candidate.producer.commit_sha = "short";
  candidate.observed_at = "yesterday";
  const errors = validateAgainstSchema(candidate);
  assert.ok(errors.some((error) => error.includes("producer.commit_sha")));
  assert.ok(errors.some((error) => error.includes("observed_at")));
});

test("unknown top-level and nested properties fail closed", () => {
  const candidate = validEnvelope();
  candidate.unreviewed = true;
  candidate.action.extra = "unexpected";
  const errors = validateAgainstSchema(candidate);
  assert.ok(errors.some((error) => error.includes("unknown property unreviewed")));
  assert.ok(errors.some((error) => error.includes("action: unknown property extra")));
});

test("receipt envelopes require explicit Ed25519 signature metadata", () => {
  const missing = validEnvelope();
  delete missing.attestation;
  assert.ok(validateAgainstSchema(missing).some((error) => error.includes("receipt stage requires attestation")));

  const badAlgorithm = validEnvelope();
  badAlgorithm.attestation.algorithm = "none";
  assert.ok(validateAgainstSchema(badAlgorithm).some((error) => error.includes("attestation.algorithm")));

  const badSignature = validEnvelope();
  badSignature.attestation.signature = "unsigned";
  assert.ok(validateAgainstSchema(badSignature).some((error) => error.includes("attestation.signature")));
});

test("intent envelopes can remain pending without a receipt attestation", () => {
  const intent = validEnvelope();
  intent.stage = "intent";
  intent.decision_state = "pending";
  delete intent.attestation;
  assert.deepEqual(validateAgainstSchema(intent), []);
});

test("method is part of the structured action identity, not a display label", () => {
  const candidate = validEnvelope();
  const intended = { type: "http", resource: "/records", method: "POST" };
  assert.equal(actionMatches(candidate, intended), true);
  assert.equal(actionMatches(candidate, { ...intended, method: "DELETE" }), false);
});

test("indeterminate stays indeterminate and is not silently promoted", () => {
  const candidate = validEnvelope();
  candidate.decision_state = "indeterminate";
  assert.deepEqual(validateAgainstSchema(candidate), []);
  assert.equal(candidate.decision_state, "indeterminate");
  assert.ok(schema.properties.decision_state.enum.includes("indeterminate"));
  assert.ok(schema.properties.decision_state.enum.includes("completed"));
});

test("schema version and lifecycle stage are explicit", () => {
  const candidate = validEnvelope();
  candidate.schema_version = 2;
  candidate.stage = "success";
  const errors = validateAgainstSchema(candidate);
  assert.ok(errors.some((error) => error.includes("schema_version")));
  assert.ok(errors.some((error) => error.includes("stage")));
});
