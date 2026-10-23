"use strict";

const REQUIRED_SUITES = ["javascript_suite", "python_descent_suite"];

/** Compare a receipt with independently obtained workflow evidence. */
function verifyExecutionEvidence({ receipt, runEvidence, artifactSha256, trustedRunEvidence = false }) {
  if (!receipt || !runEvidence || !artifactSha256 || !receipt.commit ||
      receipt.github_run_id == null || receipt.github_run_attempt == null ||
      !receipt.expected_artifact_sha256 || !runEvidence.head_sha ||
      runEvidence.run_id == null || runEvidence.run_attempt == null ||
      !runEvidence.status || !runEvidence.conclusion || !runEvidence.suiteResults) {
    return { status: "UNRESOLVED", reasons: ["required evidence is missing"] };
  }
  if (trustedRunEvidence !== true) {
    return { status: "UNTRUSTED", reasons: ["workflow metadata was not independently trusted"] };
  }
  const mismatches = [];
  if (String(receipt.commit) !== String(runEvidence.head_sha)) mismatches.push("receipt commit differs from workflow head SHA");
  if (String(receipt.github_run_id) !== String(runEvidence.run_id)) mismatches.push("workflow run ID differs");
  if (String(receipt.github_run_attempt) !== String(runEvidence.run_attempt)) mismatches.push("workflow run attempt differs");
  if (runEvidence.status !== "completed" || runEvidence.conclusion !== "success") mismatches.push("workflow did not complete successfully");
  for (const suite of REQUIRED_SUITES) {
    if (receipt[suite] !== "passed" || runEvidence.suiteResults[suite] !== "passed") mismatches.push("required suite not proven passed: " + suite);
  }
  if (receipt.expected_artifact_sha256 !== artifactSha256) mismatches.push("artifact digest differs from receipt claim");
  return mismatches.length ? { status: "MISMATCH", reasons: mismatches } : { status: "VERIFIED", reasons: [] };
}
module.exports = { REQUIRED_SUITES, verifyExecutionEvidence };
