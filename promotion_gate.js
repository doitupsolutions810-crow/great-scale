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

function evaluatePromotionEvidence(evidence) {
  const reasons = [];
  const fail = reason => reasons.push(reason);
  if (!evidence || typeof evidence !== 'object' || Array.isArray(evidence)) {
    return { eligible: false, state: 'BLOCKED', reasons: ['evidence envelope missing or malformed'] };
  }

  const { candidate, run, job, receipt, artifact } = evidence;
  if (!candidate || typeof candidate.repo !== 'string' || !candidate.repo ||
      typeof candidate.sha !== 'string' || !SHA_RE.test(candidate.sha)) {
    fail('candidate repository and full 40-character SHA are required');
  }
  if (!run || run.source !== 'github-actions-api') {
    fail('run evidence must come from the GitHub Actions API collector');
  }
  if (!run || typeof run.repository !== 'string' || run.repository !== candidate?.repo) {
    fail('run repository does not match candidate repository');
  }
  if (!run || run.workflowPath !== '.github/workflows/ci.yml') {
    fail('expected CI workflow path is not bound to this run');
  }
  if (!Number.isSafeInteger(run?.id) || run.id <= 0) {
    fail('valid workflow run ID is required');
  }
  if (!run || run.headSha !== candidate?.sha) {
    fail('workflow run head SHA does not equal candidate SHA');
  }
  if (!run || run.conclusion !== 'success') {
    fail('workflow run conclusion is not success');
  }
  if (!job || !Number.isSafeInteger(job.id) || job.id <= 0) {
    fail('valid job ID is required');
  }
  if (!job || job.conclusion !== 'success') {
    fail('test job conclusion is not success');
  }
  if (!Number.isSafeInteger(job?.runnerId) || job.runnerId <= 0 ||
      typeof job?.runnerName !== 'string' || !job.runnerName.trim()) {
    fail('observed nonzero runner identity is missing');
  }
  if (typeof job?.logsUrl !== 'string' || !/^https:\/\/github\.com\/.+\/actions\/runs\/.+\/job\/.+/.test(job.logsUrl)) {
    fail('platform job logs URL is missing or unrecognized');
  }
  if (!Array.isArray(job?.steps) || job.steps.length === 0) {
    fail('platform step records are missing');
  } else {
    const byName = new Map();
    for (const step of job.steps) {
      if (!step || typeof step.name !== 'string' || !step.name.trim()) {
        fail('malformed platform step record');
        continue;
      }
      if (byName.has(step.name)) fail(`duplicate platform step name: ${step.name}`);
      byName.set(step.name, step);
      if (step.conclusion !== 'success') fail(`platform step not successful: ${step.name}`);
    }
    for (const name of REQUIRED_STEPS) {
      if (!byName.has(name)) fail(`required workflow step missing: ${name}`);
    }
  }
  if (!receipt || receipt.schema !== 'great-scale.verification-receipt/v1') {
    fail('verification receipt schema missing or unknown');
  }
  if (!receipt || receipt.commit !== candidate?.sha) {
    fail('receipt commit does not equal candidate SHA');
  }
  if (!receipt || receipt.overall !== 'passed' ||
      receipt.javascript_suite !== 'passed' ||
      receipt.python_descent_suite !== 'passed') {
    fail('receipt does not record both required suites and overall status as passed');
  }
  if (String(receipt?.github_run_id ?? '') !== String(run?.id ?? '')) {
    fail('receipt workflow run ID does not match platform run ID');
  }
  if (receipt?.github_repository !== candidate?.repo) {
    fail('receipt repository does not match candidate repository');
  }
  if (!artifact || !Number.isSafeInteger(artifact.id) || artifact.id <= 0) {
    fail('platform artifact ID is missing');
  }
  if (artifact?.name !== 'great-scale-verification-receipt') {
    fail('expected verification receipt artifact is missing');
  }
  if (artifact?.workflowRunId !== run?.id) {
    fail('artifact is not bound to this workflow run');
  }
  if (artifact?.expired === true) {
    fail('verification receipt artifact has expired');
  }

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
