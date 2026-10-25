'use strict';

/**
 * Great Scale evidence ledger (Build ∞+9 prototype).
 * This module classifies evidence; it does not infer physical validity from a scalar.
 */
function finiteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

function assessEvidence(record) {
  const issues = [];
  if (!record || typeof record !== 'object' || Array.isArray(record)) {
    return { status: 'invalid', issues: ['record must be an object'] };
  }
  const topology = record.topology;
  const geometry = record.geometry;
  const provenance = record.provenance;
  const execution = record.execution;

  if (!topology || !finiteNumber(topology.chern) || !finiteNumber(topology.absoluteCurvature)) {
    issues.push('topology requires finite chern and absoluteCurvature');
  } else {
    const c = topology.chern;
    const a = topology.absoluteCurvature;
    const tol = finiteNumber(topology.tolerance) && topology.tolerance >= 0 ? topology.tolerance : 1e-10;
    if (a < 0) issues.push('absoluteCurvature must be nonnegative');
    if (a + tol < Math.abs(c)) issues.push('triangle-inequality violation: absoluteCurvature < abs(chern)');
    if (a === 0) {
      if (c !== 0) issues.push('zero absoluteCurvature requires zero chern');
      issues.push('topological scalar undefined when absoluteCurvature is zero');
    } else if (a > 0 && a + tol >= Math.abs(c)) {
      const eta = c / a;
      const s = (1 - eta * eta) / 4;
      if (!finiteNumber(s) || s < -tol || s > 0.25 + tol) issues.push('derived scalar outside expected range');
    }
  }

  if (!geometry || !['measured', 'unresolved', 'not-applicable'].includes(geometry.status)) {
    issues.push('geometry status must be measured, unresolved, or not-applicable');
  }
  if (!provenance || typeof provenance.commit !== 'string' || !provenance.commit.trim() ||
      typeof provenance.inputDigest !== 'string' || !provenance.inputDigest.trim()) {
    issues.push('provenance requires commit and inputDigest');
  }
  if (!execution || typeof execution.command !== 'string' || !execution.command.trim() ||
      !Number.isInteger(execution.exitCode)) {
    issues.push('execution requires command and integer exitCode');
  }

  const unresolvedGeometry = geometry && geometry.status === 'unresolved';
  const executionFailed = execution && Number.isInteger(execution.exitCode) && execution.exitCode !== 0;
  const status = issues.length ? 'invalid' :
    unresolvedGeometry ? 'incomplete' :
    executionFailed ? 'failed' : 'recorded-not-scientifically-certified';
  return {
    status,
    issues,
    derived: topology && finiteNumber(topology.chern) && finiteNumber(topology.absoluteCurvature) &&
      topology.absoluteCurvature > 0
      ? {
          eta: topology.chern / topology.absoluteCurvature,
          S: (1 - (topology.chern / topology.absoluteCurvature) ** 2) / 4
        }
      : null
  };
}

module.exports = { assessEvidence };
