"use strict";
const assert = require("node:assert/strict");
const { evaluateAuthorization } = require("./authorization_gate");

const fixture = () => ({
  proposal: { id: "proposal-42", diff_sha256: "a".repeat(64), scope: "cyclekernel:promote:colony-7" },
  approval: {
    principal_id: "operator-7", authenticated: true, role: "release-approver",
    proposal_id: "proposal-42", diff_sha256: "a".repeat(64), scope: "cyclekernel:promote:colony-7",
    nonce: "nonce_1234567890abcd", decision: "approved", issued_at: 900, expires_at: 1100, approval_count: 2
  },
  policy: { allowed_roles: ["release-approver"], required_approvals: 2, now_epoch_seconds: 1000, max_age_seconds: 300 },
  replay: { nonce_used: false, trusted_identity_evidence: true }
});
const blocked = (mutate) => { const x = fixture(); mutate(x); assert.equal(evaluateAuthorization(x).state, "BLOCKED"); };
const cases = [
  ["valid scoped authorization is eligible for review", () => assert.equal(evaluateAuthorization(fixture()).state, "ELIGIBLE_FOR_AUTHORIZED_EXECUTION_REVIEW")],
  ["missing envelope fails closed", () => assert.equal(evaluateAuthorization(null).state, "BLOCKED")],
  ["unauthenticated principal blocks", () => blocked(x => { x.approval.authenticated = false; })],
  ["untrusted identity evidence blocks", () => blocked(x => { x.replay.trusted_identity_evidence = false; })],
  ["unapproved decision blocks", () => blocked(x => { x.approval.decision = "pending"; })],
  ["proposal ID mismatch blocks", () => blocked(x => { x.approval.proposal_id = "other"; })],
  ["diff substitution blocks", () => blocked(x => { x.approval.diff_sha256 = "b".repeat(64); })],
  ["scope widening blocks", () => blocked(x => { x.approval.scope = "*"; })],
  ["unauthorized role blocks", () => blocked(x => { x.approval.role = "researcher"; })],
  ["insufficient quorum blocks", () => blocked(x => { x.approval.approval_count = 1; })],
  ["replayed nonce blocks", () => blocked(x => { x.replay.nonce_used = true; })],
  ["unknown replay state blocks", () => blocked(x => { x.replay.nonce_used = null; })],
  ["expired approval blocks", () => blocked(x => { x.policy.now_epoch_seconds = 1200; })],
  ["future-dated approval blocks", () => blocked(x => { x.approval.issued_at = 1001; })],
  ["approval outside max age blocks", () => blocked(x => { x.approval.issued_at = 600; })],
  ["malformed nonce blocks", () => blocked(x => { x.approval.nonce = "short"; })],
  ["malformed diff digest blocks", () => blocked(x => { x.proposal.diff_sha256 = "not-a-digest"; })],
  ["accessors are rejected without invoking them", () => {
    const x = fixture(); let called = false;
    Object.defineProperty(x.approval, "principal_id", { enumerable: true, get() { called = true; throw new Error("getter invoked"); } });
    assert.equal(evaluateAuthorization(x).state, "BLOCKED"); assert.equal(called, false);
  }]
];
for (const [name, test] of cases) {
  try { test(); } catch (error) { error.message = name + ": " + error.message; throw error; }
}
console.log(`authorization gate: ${cases.length}/${cases.length} checks passed`);
