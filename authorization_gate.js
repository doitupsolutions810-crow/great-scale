"use strict";

const crypto = require("node:crypto");
const SHA256_RE = /^[0-9a-f]{64}$/;

function record(value, keys) {
  if (!value || typeof value !== "object" || Array.isArray(value) ||
      Object.getPrototypeOf(value) !== Object.prototype) return null;
  const own = Reflect.ownKeys(value);
  if (own.length !== keys.length || own.some(k => typeof k !== "string" || !keys.includes(k))) return null;
  const out = {};
  for (const key of keys) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, "value")) return null;
    out[key] = descriptor.value;
  }
  return out;
}

/**
 * Structural authorization policy gate. It does not authenticate identities,
 * verify signatures, or atomically consume nonces. The caller must do those
 * operations through a trusted identity provider and durable replay store.
 */
function denseStringArray(value) {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype || value.length < 1 || value.length > 100) return null;
  const keys = Reflect.ownKeys(value);
  if (keys.length !== value.length + 1 || keys.some(k => k !== "length" && (typeof k !== "string" || !/^(0|[1-9][0-9]*)$/.test(k) || Number(k) >= value.length))) return null;
  const result = [];
  for (let i = 0; i < value.length; i++) {
    const descriptor = Object.getOwnPropertyDescriptor(value, String(i));
    if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, "value") ||
        typeof descriptor.value !== "string" || !descriptor.value.trim()) return null;
    result.push(descriptor.value);
  }
  return result;
}

function evaluateAuthorization(input) {
  const envelope = record(input, ["proposal", "approval", "policy", "replay"]);
  if (!envelope) return { state: "BLOCKED", reasons: ["authorization envelope missing or malformed"] };
  const proposal = record(envelope.proposal, ["id", "diff_sha256", "scope"]);
  const approval = record(envelope.approval, [
    "principal_id", "authenticated", "role", "proposal_id", "diff_sha256",
    "scope", "nonce", "decision", "issued_at", "expires_at", "approval_count"
  ]);
  const policy = record(envelope.policy, ["allowed_roles", "required_approvals", "now_epoch_seconds", "max_age_seconds"]);
  const replay = record(envelope.replay, ["nonce_used", "trusted_identity_evidence"]);
  const reasons = [];
  if (!proposal || !approval || !policy || !replay) {
    return { state: "BLOCKED", reasons: ["authorization records must have exact fields and plain data properties"] };
  }
  if (typeof proposal.id !== "string" || !proposal.id.trim() ||
      !SHA256_RE.test(String(proposal.diff_sha256)) ||
      typeof proposal.scope !== "string" || !proposal.scope.trim()) {
    reasons.push("proposal identity, diff digest, and scope are required");
  }
  if (typeof approval.principal_id !== "string" || !approval.principal_id.trim()) reasons.push("authenticated principal identity is missing");
  if (approval.authenticated !== true || replay.trusted_identity_evidence !== true) reasons.push("identity evidence is not independently trusted");
  const allowedRoles = denseStringArray(policy.allowed_roles);
  if (!allowedRoles) {
    reasons.push("policy must name a dense plain array of allowed roles");
  } else if (!allowedRoles.includes(approval.role)) {
    reasons.push("principal role is not authorized by policy");
  }
  if (approval.decision !== "approved") reasons.push("approval decision is not approved");
  if (approval.proposal_id !== proposal.id) reasons.push("approval is bound to a different proposal");
  if (approval.diff_sha256 !== proposal.diff_sha256) reasons.push("approval is bound to a different diff digest");
  if (approval.scope !== proposal.scope) reasons.push("approval scope differs from proposed action");
  if (typeof approval.nonce !== "string" || !/^[A-Za-z0-9_-]{16,128}$/.test(approval.nonce)) reasons.push("approval nonce is missing or malformed");
  if (replay.nonce_used !== false) reasons.push("approval nonce is already used or replay state is unknown");
  if (!Number.isSafeInteger(policy.required_approvals) || policy.required_approvals < 1 ||
      !Number.isSafeInteger(approval.approval_count) || approval.approval_count < policy.required_approvals) {
    reasons.push("approval quorum is not satisfied");
  }
  if (!Number.isFinite(policy.now_epoch_seconds) || !Number.isFinite(policy.max_age_seconds) || policy.max_age_seconds <= 0 ||
      !Number.isFinite(approval.issued_at) || !Number.isFinite(approval.expires_at)) {
    reasons.push("approval validity window is malformed");
  } else {
    if (approval.issued_at > policy.now_epoch_seconds) reasons.push("approval was issued in the future");
    if (policy.now_epoch_seconds >= approval.expires_at) reasons.push("approval has expired");
    if (approval.expires_at <= approval.issued_at) reasons.push("approval expiry must follow issue time");
    if (policy.now_epoch_seconds - approval.issued_at > policy.max_age_seconds) reasons.push("approval exceeds maximum allowed age");
  }
  if (reasons.length) return { state: "BLOCKED", reasons };
  return {
    state: "ELIGIBLE_FOR_AUTHORIZED_EXECUTION_REVIEW",
    reasons: [],
    binding: {
      proposalId: proposal.id,
      diffSha256: proposal.diff_sha256,
      scope: proposal.scope,
      principalId: approval.principal_id,
      role: approval.role,
      nonce: approval.nonce,
      approvalCount: approval.approval_count
    },
    caveat: "Structural gate only: an authenticated collector and atomic durable nonce consumption are required before execution. Trust/confidence scores are not authorization."
  };
}

module.exports = { evaluateAuthorization };
