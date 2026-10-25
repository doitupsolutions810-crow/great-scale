'use strict';

/**
 * Evidence Verification Gate.
 * A supplied exit code is only a claim until bound to an observed run record.
 * This gate does not certify scientific truth; it checks minimum auditability.
 */
function verifyExecutionEvidence(evidence) {
  const issues = [];
  if (!evidence || typeof evidence !== 'object' || Array.isArray(evidence)) {
    return { status: 'unverified', issues: ['execution evidence must be an object'] };
  }
  if (typeof evidence.commit !== 'string' || !/^[0-9a-f]{7,40}$/i.test(evidence.commit)) {
    issues.push('commit must be a hexadecimal Git revision');
  }
  if (typeof evidence.command !== 'string' || !evidence.command.trim()) {
    issues.push('command is required');
  }
  if (!Number.isInteger(evidence.exitCode)) issues.push('observed integer exitCode is required');
  if (typeof evidence.runId !== 'string' || !evidence.runId.trim()) {
    issues.push('runId is required to identify the execution');
  }
  if (typeof evidence.outputDigest !== 'string' || !/^sha256:[0-9a-f]{64}$/i.test(evidence.outputDigest)) {
    issues.push('outputDigest must be a SHA-256 digest of captured output');
  }
  if (typeof evidence.startedAt !== 'string' || Number.isNaN(Date.parse(evidence.startedAt))) {
    issues.push('valid startedAt timestamp is required');
  }
  if (issues.length) return { status: 'unverified', issues };
  return {
    status: evidence.exitCode === 0 ? 'execution-evidence-complete' : 'execution-failed',
    issues: [],
    commit: evidence.commit,
    runId: evidence.runId,
    exitCode: evidence.exitCode
  };
}

module.exports = { verifyExecutionEvidence };
