'use strict';

const fs = require('node:fs');

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
const REPO_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const UTC_ISO_SECONDS_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/;

function jobLogsUrlMatches(value, repository, runId, jobId) {
  if (typeof value !== 'string' || typeof repository !== 'string' ||
      !Number.isSafeInteger(runId) || !Number.isSafeInteger(jobId)) return false;
  let url;
  try { url = new URL(value); } catch { return false; }
  return url.protocol === 'https:' && url.hostname === 'github.com' &&
    url.port === '' && url.username === '' && url.password === '' &&
    url.search === '' && url.hash === '' &&
    url.pathname === `/${repository}/actions/runs/${runId}/job/${jobId}`;
}

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

const MAX_EVIDENCE_BYTES = 1048576;
const MAX_EVIDENCE_DEPTH = 64;
const MAX_EVIDENCE_KEYS_PER_OBJECT = 32;
const MAX_EVIDENCE_ARRAY_ITEMS = 10000;
const MAX_EVIDENCE_VALUES = 100000;

// Scan JSON tokens iteratively before materialization. Duplicate decoded keys
// are rejected so downstream consumers cannot disagree about which value wins.
function scanEvidenceJson(raw) {
  const stack = [];
  let i = 0, rootDone = false, values = 0;
  const whitespace = c => c === 32 || c === 9 || c === 10 || c === 13;
  const skipSpace = () => { while (i < raw.length && whitespace(raw.charCodeAt(i))) i++; };
  const stringEnd = start => {
    let j = start + 1;
    while (j < raw.length) {
      if (raw[j] === '\\') { j += 2; continue; }
      if (raw[j] === '"') return j + 1;
      j++;
    }
    return raw.length;
  };
  while (true) {
    skipSpace();
    if (i >= raw.length) break;
    const frame = stack[stack.length - 1];
    if (frame && frame.type === 'object' && (frame.state === 'keyOrEnd' || frame.state === 'key')) {
      if (raw[i] === '}') { stack.pop(); i++; continue; }
      if (raw[i] !== '"') throw new Error('invalid JSON evidence');
      const end = stringEnd(i);
      let key;
      try { key = JSON.parse(raw.slice(i, end)); } catch { throw new Error('invalid JSON evidence'); }
      if (frame.keys.has(key)) throw new Error('duplicate JSON object key');
      frame.keys.add(key);
      if (frame.keys.size > MAX_EVIDENCE_KEYS_PER_OBJECT) throw new Error('evidence object key limit exceeded');
      frame.state = 'colon'; i = end; continue;
    }
    if (frame && frame.type === 'object' && frame.state === 'colon') {
      if (raw[i] !== ':') throw new Error('invalid JSON evidence');
      i++; frame.state = 'value'; continue;
    }
    if (frame && frame.state === 'commaOrEnd') {
      if (raw[i] === ',') { i++; frame.state = frame.type === 'object' ? 'key' : 'value'; }
      else if ((frame.type === 'object' && raw[i] === '}') || (frame.type === 'array' && raw[i] === ']')) {
        stack.pop(); i++;
      } else throw new Error('invalid JSON evidence');
      continue;
    }
    if (frame && frame.type === 'array' && frame.state === 'valueOrEnd' && raw[i] === ']') {
      stack.pop(); i++; continue;
    }
    if (!frame && rootDone) throw new Error('invalid JSON evidence');
    if (++values > MAX_EVIDENCE_VALUES) throw new Error('evidence JSON value limit exceeded');
    if (frame && frame.type === 'array' && ++frame.items > MAX_EVIDENCE_ARRAY_ITEMS) {
      throw new Error('evidence array item limit exceeded');
    }
    if (frame) frame.state = 'commaOrEnd';
    else rootDone = true;
    if (raw[i] === '{') {
      if (stack.length >= MAX_EVIDENCE_DEPTH) throw new Error('evidence JSON depth limit exceeded');
      stack.push({type:'object', state:'keyOrEnd', keys:new Set()}); i++;
    } else if (raw[i] === '[') {
      if (stack.length >= MAX_EVIDENCE_DEPTH) throw new Error('evidence JSON depth limit exceeded');
      stack.push({type:'array', state:'valueOrEnd', items:0}); i++;
    } else if (raw[i] === '"') {
      i = stringEnd(i);
    } else {
      const start = i;
      while (i < raw.length && !whitespace(raw.charCodeAt(i)) && raw[i] !== ',' && raw[i] !== ']' && raw[i] !== '}') i++;
      if (i === start) throw new Error('invalid JSON evidence');
    }
  }
}
function parseBoundedEvidenceJson(raw) {
  if (typeof raw !== 'string' || raw.length > MAX_EVIDENCE_BYTES ||
      Buffer.byteLength(raw, 'utf8') > MAX_EVIDENCE_BYTES) {
    throw new Error('evidence JSON byte limit exceeded');
  }
  scanEvidenceJson(raw);
  try { return JSON.parse(raw); }
  catch { throw new Error('invalid JSON evidence'); }
}

function evaluatePromotionEvidence(evidence) {
  const reasons = [];
  if (!evidence || typeof evidence !== 'object' || Array.isArray(evidence)) {
    return { eligible: false, state: 'BLOCKED', reasons: ['evidence envelope missing or malformed'] };
  }
  const env = plainDataRecord(evidence, ['candidate', 'pullRequest', 'run', 'job', 'receipt', 'artifact'], 'evidence envelope', reasons);
  if (!env) return { eligible: false, state: 'BLOCKED', reasons };

  const candidate = plainDataRecord(env.candidate, ['repo', 'sha'], 'candidate', reasons);
  const pullRequest = plainDataRecord(env.pullRequest, ['number', 'state', 'headRepository', 'headSha', 'mergeCommitSha'], 'pull request snapshot', reasons);
  const run = plainDataRecord(env.run, ['source', 'repository', 'workflowPath', 'event', 'id', 'runAttempt', 'headSha', 'conclusion'], 'run', reasons);
  const job = plainDataRecord(env.job, ['id', 'conclusion', 'runnerId', 'runnerName', 'logsUrl', 'steps'], 'job', reasons);
  const receipt = plainDataRecord(env.receipt, ['schema', 'commit', 'node', 'npm', 'python', 'javascript_suite', 'python_descent_suite', 'overall', 'created_utc', 'github_run_id', 'github_run_attempt', 'github_repository', 'github_sha', 'runner_name'], 'receipt', reasons);
  const artifact = plainDataRecord(env.artifact, ['id', 'name', 'workflowRunId', 'expired'], 'artifact', reasons);
  if (!candidate || !pullRequest || !run || !job || !receipt || !artifact) {
    return { eligible: false, state: 'BLOCKED', reasons };
  }

  if (typeof candidate.repo !== 'string' || !REPO_RE.test(candidate.repo) ||
      typeof candidate.sha !== 'string' || !SHA_RE.test(candidate.sha)) {
    reasons.push('candidate repository in owner/repository form and full 40-character SHA are required');
  }
  if (!Number.isSafeInteger(pullRequest.number) || pullRequest.number <= 0) reasons.push('valid pull request number is required');
  if (pullRequest.state !== 'open') reasons.push('pull request must still be open at evidence collection time');
  if (typeof pullRequest.headRepository !== 'string' || pullRequest.headRepository !== candidate.repo) reasons.push('pull request head repository does not match candidate repository');
  if (typeof pullRequest.headSha !== 'string' || !SHA_RE.test(pullRequest.headSha) || pullRequest.headSha !== candidate.sha) reasons.push('current pull request head SHA does not equal candidate head SHA');
  if (typeof pullRequest.mergeCommitSha !== 'string' || !SHA_RE.test(pullRequest.mergeCommitSha)) reasons.push('current pull request merge-test SHA is missing or malformed');
  if (run.source !== 'github-actions-api') reasons.push('run evidence must come from the GitHub Actions API collector');
  if (run.event !== 'pull_request') reasons.push('run must be associated with a pull_request event');
  if (!Number.isSafeInteger(run.runAttempt) || run.runAttempt <= 0) reasons.push('valid workflow run attempt is required');
  if (typeof run.repository !== 'string' || run.repository !== candidate.repo) reasons.push('run repository does not match candidate repository');
  if (run.workflowPath !== '.github/workflows/ci.yml') reasons.push('expected CI workflow path is not bound to this run');
  if (!Number.isSafeInteger(run.id) || run.id <= 0) reasons.push('valid workflow run ID is required');
  if (run.headSha !== candidate.sha) reasons.push('workflow run head SHA does not equal the pull request source head SHA');
  if (run.conclusion !== 'success') reasons.push('workflow run conclusion is not success');
  if (!Number.isSafeInteger(job.id) || job.id <= 0) reasons.push('valid job ID is required');
  if (job.conclusion !== 'success') reasons.push('test job conclusion is not success');
  if (!Number.isSafeInteger(job.runnerId) || job.runnerId <= 0 ||
      typeof job.runnerName !== 'string' || !job.runnerName.trim()) {
    reasons.push('observed nonzero runner identity is missing');
  }
  if (!jobLogsUrlMatches(job.logsUrl, candidate.repo, run.id, job.id)) {
    reasons.push('platform job logs URL is not bound to the candidate repository, workflow run, and job ID');
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
  if (receipt.commit !== pullRequest.mergeCommitSha) reasons.push('receipt checkout commit does not equal the current pull request merge-test SHA');
  if (receipt.github_sha !== pullRequest.mergeCommitSha) reasons.push('receipt GitHub SHA does not equal the current pull request merge-test SHA');
  if (String(receipt.github_run_attempt ?? '') !== String(run.runAttempt ?? '')) reasons.push('receipt run attempt does not match platform run attempt');
  const receiptTime = typeof receipt.created_utc === 'string' ? Date.parse(receipt.created_utc) : NaN;
  if (!Number.isFinite(receiptTime) ||
      !UTC_ISO_SECONDS_RE.test(receipt.created_utc) ||
      !Number.isFinite(Date.parse(receipt.created_utc)) ||
      new Date(receiptTime).toISOString() !== receipt.created_utc) {
    reasons.push('receipt creation timestamp must be a valid UTC ISO-8601 timestamp');
  } else if (receiptTime > Date.now() + 5 * 60 * 1000) {
    reasons.push('receipt creation timestamp is too far in the future');
  }
  for (const key of ['node', 'npm', 'python', 'runner_name']) {
    if (typeof receipt[key] !== 'string' || !receipt[key].trim() || receipt[key] === 'unavailable') reasons.push('receipt runtime field is missing or unavailable: ' + key);
  }
  if (typeof job.runnerName === 'string' && typeof receipt.runner_name === 'string' &&
      receipt.runner_name !== job.runnerName) {
    reasons.push('receipt runner name does not match the observed platform job runner name');
  }
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
    binding: { repository: candidate.repo, pullRequestHeadSha: candidate.sha, testedMergeSha: run.headSha, pullRequestNumber: pullRequest.number, runId: run.id, runAttempt: run.runAttempt, jobId: job.id, artifactId: artifact.id },
    caveat: 'Structural gate only: the pull-request head and merge-test SHA are separately bound at collection time. A later merge must recheck both identities; authenticated collection, test adequacy, human review, and deployment authorization remain separate obligations.',
  };
}

module.exports = { evaluatePromotionEvidence, REQUIRED_STEPS };

if (require.main === module) {
  const evidencePath = process.argv[2];
  if (!evidencePath) {
    console.error('Usage: node promotion_gate.js <authenticated-platform-evidence.json>');
    process.exitCode = 2;
  } else {
    try {
      const fd = fs.openSync(evidencePath, 'r');
      let raw;
      try {
        const stat = fs.fstatSync(fd);
        if (stat.size > MAX_EVIDENCE_BYTES) throw new Error('evidence JSON byte limit exceeded');
        // Read at most cap+1 bytes so a file that grows after fstat cannot
        // force an unbounded allocation before the limit is checked.
        const buffer = Buffer.alloc(MAX_EVIDENCE_BYTES + 1);
        const bytesRead = fs.readSync(fd, buffer, 0, buffer.length, 0);
        if (bytesRead > MAX_EVIDENCE_BYTES) throw new Error('evidence JSON byte limit exceeded');
        raw = buffer.subarray(0, bytesRead).toString('utf8');
      } finally {
        fs.closeSync(fd);
      }
      const evidence = parseBoundedEvidenceJson(raw);
      const result = evaluatePromotionEvidence(evidence);
      console.log(JSON.stringify(result, null, 2));
      if (!result.eligible) process.exitCode = 1;
    } catch (error) {
      console.error(`Promotion evidence could not be read or parsed: ${error.message}`);
      process.exitCode = 2;
    }
  }
}
