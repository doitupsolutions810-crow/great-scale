'use strict';

const crypto = require('node:crypto');

/**
 * Evidence Verification Gate.
 * Verifies the internal integrity of a supplied run record.
 * It does not authenticate the run source or certify scientific truth.
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
  if (typeof evidence.capturedOutput !== 'string') {
    issues.push('capturedOutput string is required to verify the digest');
  }
  if (typeof evidence.outputDigest !== 'string' || !/^sha256:[0-9a-f]{64}$/i.test(evidence.outputDigest)) {
    issues.push('outputDigest must be a SHA-256 digest of captured output');
  } else if (typeof evidence.capturedOutput === 'string') {
    const actual = 'sha256:' + crypto.createHash('sha256').update(evidence.capturedOutput, 'utf8').digest('hex');
    if (actual.toLowerCase() !== evidence.outputDigest.toLowerCase()) {
      issues.push('outputDigest does not match capturedOutput');
    }
  }
  if (typeof evidence.startedAt !== 'string' || Number.isNaN(Date.parse(evidence.startedAt))) {
    issues.push('valid startedAt timestamp is required');
  }
  if (issues.length) return { status: 'unverified', issues };
  return {
    status: evidence.exitCode === 0 ? 'record-integrity-valid' : 'execution-failed',
    issues: [],
    commit: evidence.commit,
    runId: evidence.runId,
    exitCode: evidence.exitCode
  };
}

module.exports = { verifyExecutionEvidence };
