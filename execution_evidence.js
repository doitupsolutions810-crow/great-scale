"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const POLICY_PATH = path.join(__dirname, "verification-policy.json");
const POLICY_SHA256 = crypto.createHash("sha256").update(fs.readFileSync(POLICY_PATH)).digest("hex");
const POLICY = JSON.parse(fs.readFileSync(POLICY_PATH, "utf8"));
const REQUIRED_SUITES = POLICY.requiredSuites;
const EXPECTED_REPOSITORY = "doitupsolutions810-crow/great-scale";

/**
 * Compare a receipt with independently obtained workflow evidence.
 * This is a decision function, not an authentication client. The caller must
 * authenticate GitHub API data and calculate artifactSha256 from actual bytes.
 */
function verifyExecutionEvidence({ receipt, runEvidence, artifactSha256, trustedRunEvidence = false }) {
  if (!receipt || !runEvidence || !/^[0-9a-f]{64}$/.test(String(artifactSha256 || "")) ||
      !receipt.commit || receipt.github_run_id == null || receipt.github_run_attempt == null ||
      !/^[0-9a-f]{64}$/.test(String(receipt.expected_artifact_sha256 || "")) ||
      !receipt.test_policy_sha256 || !runEvidence.test_policy_sha256 ||
      !runEvidence.tested_sha || !runEvidence.source_head_sha || runEvidence.run_id == null || runEvidence.run_attempt == null ||
      !runEvidence.status || !runEvidence.conclusion || !runEvidence.suiteResults ||
      !runEvidence.repository || !runEvidence.workflow_path) {
    return { status: "UNRESOLVED", reasons: ["required evidence is missing or malformed"] };
  }
  if (trustedRunEvidence !== true) {
    return { status: "UNTRUSTED", reasons: ["workflow metadata was not independently trusted"] };
  }
  const mismatches = [];
  if (String(receipt.commit) !== String(runEvidence.tested_sha)) mismatches.push("receipt commit differs from exact tested commit SHA");
  if (String(receipt.github_sha) !== String(runEvidence.tested_sha)) mismatches.push("receipt GitHub SHA differs from exact tested commit SHA");
  if (String(receipt.github_head_sha) !== String(runEvidence.source_head_sha)) mismatches.push("receipt source-head SHA differs from pull-request source head SHA");
  if (String(receipt.github_run_id) !== String(runEvidence.run_id)) mismatches.push("workflow run ID differs");
  if (String(receipt.github_run_attempt) !== String(runEvidence.run_attempt)) mismatches.push("workflow run attempt differs");
  if (runEvidence.repository !== EXPECTED_REPOSITORY) mismatches.push("workflow repository differs from expected repository");
  if (runEvidence.workflow_path !== POLICY.workflowPath) mismatches.push("workflow path differs from canonical policy");
  if (receipt.test_policy_sha256 !== POLICY_SHA256 || runEvidence.test_policy_sha256 !== POLICY_SHA256) {
    mismatches.push("receipt or run evidence does not bind to the checked-out test policy");
  }
  if (runEvidence.status !== "completed" || runEvidence.conclusion !== "success") mismatches.push("workflow did not complete successfully");
  for (const suite of REQUIRED_SUITES) {
    if (receipt[suite] !== "passed" || runEvidence.suiteResults[suite] !== "passed") {
      mismatches.push("required suite not proven passed: " + suite);
    }
  }
  if (receipt.expected_artifact_sha256 !== artifactSha256) mismatches.push("artifact digest differs from receipt claim");
  return mismatches.length ? { status: "MISMATCH", reasons: mismatches } : { status: "VERIFIED", reasons: [] };
}

module.exports = { REQUIRED_SUITES, POLICY_SHA256, verifyExecutionEvidence };
