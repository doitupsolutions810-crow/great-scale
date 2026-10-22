'use strict';

// Structural promotion policy. This does not authenticate GitHub evidence itself.
// The caller must obtain platform fields from an authenticated GitHub API/client,
// bind them to the exact candidate commit, and pass the fetched data here.
// The output is review eligibility, not permission to auto-merge or deploy.

const REQUIRED_STEPS = [
  'Checkout source',
  'Set up Node.js',
  'Set up Python',
  'Run the canonical verification script',
  'Upload commit-bound verification receipt',
];
const SHA_RE = /^[0-9a-f]{40}$/i;

function plainDataRecord(value, expectedKeys, label, reasons) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.getPrototypeOf(value) !== Object.prototype) {
    reasons.push(`${label} must be a plain object`);
    return null;
  }
  const keys = Reflect.ownKeys(value);
  const expected = [...expectedKeys].sort();
  const actual = keys.filter(k => typeof k === 'string').sort();
  if (keys.some(k => typeof k !== 'string') ||
      JSON.stringify(actual) !== JSON.stringify(expected)) {
    reasons.push(`${label} has a missing or unexpected field`);
    return null;
  }
  const out = {};
  for (const key of expectedKeys) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, 'value')) {
      reasons.push(`${label} accessors are not allowed`);
      return null;
    }
    out[key] = descriptor.value;
  }
  return out;
}

function plainDenseArray(value, label, reasons) {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) {
    reasons.push(`${label} must be an ordinary array`);
    return null;
  }
  if (value.length > 10000) {
    reasons.push(`${label} exceeds the item limit`);
    return null;
  }
  const keys = Reflect.ownKeys(value);
  if (keys.length !== value.length + 1 ||
      keys.some(k => k !== 'length' && (typeof k !== 'string' ||
        !/^(0|[1-9][0-9]*)$/.test(k) || Number(k) >= value.length))) {
    reasons.push(`${label} must be dense and have no custom properties`);
    return null;
  }
  const out = [];
  for (let i = 0; i < value.length; i++) {
    const descriptor = Object.getOwnPropertyDescriptor(value, String(i));
    if (!descriptor || !Object.prototype.hasOwnProperty.call(descriptor, 'value')) {
      reasons.push(`${label} elements must be own data properties`);
      return null;
    }
    out.push(descriptor.value);
  }
  return out;
}

function evaluatePromotionEvidence(evidence) {
  const reasons = [];
  if (!evidence || typeof evidence !== 'object' || Array.isArray(evidence)) {
    return { eligible: false, state: 'BLOCKED', reasons: ['evidence envelope missing or malformed'] };
  }
  const env = plainDataRecord(evidence, ['candidate', 'run', 'job', 'receipt', 'artifact'], 'evidence envelope', reasons);
  if (!env) return { eligible: false, state: 'BLOCKED', reasons };

  const candidate = plainDataRecord(env.candidate, ['repo', 'sha'], 'candidate', reasons);
  const run = plainDataRecord(env.run, ['source', 'repository', 'workflowPath', 'id', 'headSha', 'conclusion'], 'run', reasons);
  const job = plainDataRecord(env.job, ['id', 'conclusion', 'runnerId', 'runnerName', 'logsUrl', 'steps'], 'job', reasons);
  const receipt = plainDataRecord(env.receipt, ['schema', 'commit', 'overall', 'javascript_suite', 'python_descent_suite', 'github_run_id', 'github_repository'], 'receipt', reasons);
  const artifact = plainDataRecord(env.artifact, ['id', 'name', 'workflowRunId', 'expired'], 'artifact', reasons);
  if (!candidate || !run || !job || !receipt || !artifact) {
    return { eligible: false, state: 'BLOCKED', reasons };
  }

  if (typeof candidate.repo !== 'string' || !candidate.repo ||
      typeof candidate.sha !== 'string' || !SHA_RE.test(candidate.sha)) {
    reasons.push('candidate repository and full 40-character SHA are required');
  }
  if (run.source !== 'github-actions-api') reasons.push('run evidence must come from the GitHub Actions API collector');
  if (typeof run.repository !== 'string' || run.repository !== candidate.repo) reasons.push('run repository does not match candidate repository');
  if (run.workflowPath !== '.github/workflows/ci.yml') reasons.push('expected CI workflow path is not bound to this run');
  if (!Number.isSafeInteger(run.id) || run.id <= 0) reasons.push('valid workflow run ID is required');
  if (run.headSha !== candidate.sha) reasons.push('workflow run head SHA does not equal candidate SHA');
  if (run.conclusion !== 'success') reasons.push('workflow run conclusion is not success');
  if (!Number.isSafeInteger(job.id) || job.id <= 0) reasons.push('valid job ID is required');
  if (job.conclusion !== 'success') reasons.push('test job conclusion is not success');
  if (!Number.isSafeInteger(job.runnerId) || job.runnerId <= 0 ||
      typeof job.runnerName !== 'string' || !job.runnerName.trim()) {
    reasons.push('observed nonzero runner identity is missing');
  }
  if (typeof job.logsUrl !== 'string' ||
      !/^https:\/\/github\.com\/.+\/actions\/runs\/.+\/job\/.+/.test(job.logsUrl)) {
    reasons.push('platform job logs URL is missing or unrecognized');
  }

  const rawSteps = plainDenseArray(job.steps, 'platform steps', reasons);
  if (!rawSteps || rawSteps.length === 0) {
    if (rawSteps && rawSteps.length === 0) reasons.push('platform step records are missing');
  } else {
    const byName = new Map();
    for (const raw of rawSteps) {
      const step = plainDataRecord(raw, ['name', 'conclusion'], 'platform step', reasons);
      if (!step) continue;
      if (typeof step.name !== 'string' || !step.name.trim()) {
        reasons.push('platform step name is malformed');
        continue;
      }
      if (byName.has(step.name)) reasons.push(`duplicate platform step name: ${step.name}`);
      byName.set(step.name, step);
      if (step.conclusion !== 'success') reasons.push(`platform step not successful: ${step.name}`);
    }
    for (const name of REQUIRED_STEPS) {
      if (!byName.has(name)) reasons.push(`required workflow step missing: ${name}`);
    }
  }

  if (receipt.schema !== 'great-scale.verification-receipt/v1') reasons.push('verification receipt schema missing or unknown');
  if (receipt.commit !== candidate.sha) reasons.push('receipt commit does not equal candidate SHA');
  if (receipt.overall !== 'passed' || receipt.javascript_suite !== 'passed' ||
      receipt.python_descent_suite !== 'passed') {
    reasons.push('receipt does not record both required suites and overall status as passed');
  }
  if (String(receipt.github_run_id ?? '') !== String(run.id ?? '')) reasons.push('receipt workflow run ID does not match platform run ID');
  if (receipt.github_repository !== candidate.repo) reasons.push('receipt repository does not match candidate repository');
  if (!Number.isSafeInteger(artifact.id) || artifact.id <= 0) reasons.push('platform artifact ID is missing');
  if (artifact.name !== 'great-scale-verification-receipt') reasons.push('expected verification receipt artifact is missing');
  if (artifact.workflowRunId !== run.id) reasons.push('artifact is not bound to this workflow run');
  if (artifact.expired !== false) reasons.push('artifact must be explicitly confirmed not expired');

  if (reasons.length) return { eligible: false, state: 'BLOCKED', reasons };
  return {
    eligible: true,
    state: 'ELIGIBLE_FOR_PROMOTION_REVIEW',
    reasons: [],
    binding: { repository: candidate.repo, sha: candidate.sha, runId: run.id, jobId: job.id, artifactId: artifact.id },
    caveat: 'Structural gate only: authenticated evidence collection, semantic test adequacy, human review, and deployment authorization remain separate obligations.',
  };
}

module.exports = { evaluatePromotionEvidence, REQUIRED_STEPS };
