"use strict";
const assert = require("node:assert/strict");
const { verifyExecutionEvidence, POLICY_SHA256 } = require("./execution_evidence");

const digest = "a".repeat(64);
const receipt = {
  commit: "abc123",
  github_run_id: "9001",
  github_run_attempt: "2",
  javascript_suite: "passed",
  python_descent_suite: "passed",
  expected_artifact_sha256: digest,
  test_policy_sha256: POLICY_SHA256
};
const runEvidence = {
  head_sha: "abc123",
  run_id: 9001,
  run_attempt: 2,
  status: "completed",
  conclusion: "success",
  repository: "doitupsolutions810-crow/great-scale",
  workflow_path: ".github/workflows/ci.yml",
  test_policy_sha256: POLICY_SHA256,
  suiteResults: { javascript_suite: "passed", python_descent_suite: "passed" }
};
const evaluate = (receiptPatch = {}, runPatch = {}, opts = {}) =>
  verifyExecutionEvidence({
    receipt: { ...receipt, ...receiptPatch },
    runEvidence: { ...runEvidence, ...runPatch },
    artifactSha256: opts.artifactSha256 || digest,
    trustedRunEvidence: opts.trustedRunEvidence ?? true
  });

const cases = [
  ["untrusted source defaults to UNTRUSTED", () =>
    assert.equal(verifyExecutionEvidence({ receipt, runEvidence, artifactSha256: digest }).status, "UNTRUSTED")],
  ["matching evidence verifies", () => assert.equal(evaluate().status, "VERIFIED")],
  ["commit mismatch blocks", () => assert.equal(evaluate({ commit: "other" }).status, "MISMATCH")],
  ["queued workflow blocks", () => assert.equal(evaluate({}, { status: "queued", conclusion: "null" }).status, "MISMATCH")],
  ["missing suite blocks", () => assert.equal(evaluate({}, { suiteResults: { javascript_suite: "passed", python_descent_suite: "not_run" } }).status, "MISMATCH")],
  ["artifact digest mismatch blocks", () => assert.equal(evaluate({}, {}, { artifactSha256: "b".repeat(64) }).status, "MISMATCH")],
  ["attempt mismatch blocks", () => assert.equal(evaluate({ github_run_attempt: "1" }).status, "MISMATCH")],
  ["missing receipt evidence is unresolved", () => assert.equal(verifyExecutionEvidence({ receipt: {}, runEvidence, artifactSha256: digest, trustedRunEvidence: true }).status, "UNRESOLVED")],
  ["explicitly untrusted evidence blocks", () => assert.equal(evaluate({}, {}, { trustedRunEvidence: false }).status, "UNTRUSTED")],
  ["wrong repository blocks", () => assert.equal(evaluate({}, { repository: "attacker/fork" }).status, "MISMATCH")],
  ["wrong workflow path blocks", () => assert.equal(evaluate({}, { workflow_path: ".github/workflows/other.yml" }).status, "MISMATCH")],
  ["receipt policy hash mismatch blocks", () => assert.equal(evaluate({ test_policy_sha256: "0".repeat(64) }).status, "MISMATCH")],
  ["run policy hash mismatch blocks", () => assert.equal(evaluate({}, { test_policy_sha256: "0".repeat(64) }).status, "MISMATCH")],
  ["malformed digest is unresolved", () => assert.equal(evaluate({}, {}, { artifactSha256: "not-a-sha256" }).status, "UNRESOLVED")]
];
for (const [name, fn] of cases) {
  try { fn(); }
  catch (error) { error.message = name + ": " + error.message; throw error; }
}
console.log(`execution evidence verifier: ${cases.length}/${cases.length} checks passed`);
