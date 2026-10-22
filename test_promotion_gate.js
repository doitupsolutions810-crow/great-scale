'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { evaluatePromotionEvidence, REQUIRED_STEPS } = require('./promotion_gate');

const SHA = 'a'.repeat(40);
const fixture = () => ({
  candidate: { repo: 'doitupsolutions810-crow/great-scale', sha: SHA },
  pullRequest: { number: 89, state: 'open', headRepository: 'doitupsolutions810-crow/great-scale', headSha: SHA },
  pullRequest: { number: 89, state: 'open', headRepository: 'doitupsolutions810-crow/great-scale', headSha: SHA },
  run: {
    source: 'github-actions-api',
    repository: 'doitupsolutions810-crow/great-scale',
    workflowPath: '.github/workflows/ci.yml',
    id: 12345,
    headSha: SHA,
    conclusion: 'success',
  },
  job: {
    id: 98765,
    conclusion: 'success',
    runnerId: 42,
    runnerName: 'github-hosted-runner-1',
    logsUrl: 'https://github.com/doitupsolutions810-crow/great-scale/actions/runs/12345/job/98765',
    steps: REQUIRED_STEPS.map(name => ({ name, conclusion: 'success' })),
  },
  receipt: {
    schema: 'great-scale.verification-receipt/v1',
    commit: SHA,
    overall: 'passed',
    javascript_suite: 'passed',
    python_descent_suite: 'passed',
    github_run_id: '12345',
    github_repository: 'doitupsolutions810-crow/great-scale',
  },
  artifact: {
    id: 45678,
    name: 'great-scale-verification-receipt',
    workflowRunId: 12345,
    expired: false,
  },
});

let passed = 0, failed = 0;
const results = [];
function test(name, fn) {
  try { fn(); passed++; results.push({ name, ok: true }); }
  catch (e) { failed++; results.push({ name, ok: false, error: e.message }); }
}
function blocked(mutator) {
  const x = fixture(); mutator(x);
  assert.equal(evaluatePromotionEvidence(x).eligible, false);
}
test('complete evidence is eligible for review only', () => {
  const r = evaluatePromotionEvidence(fixture());
  assert.equal(r.eligible, true);
  assert.equal(r.state, 'ELIGIBLE_FOR_PROMOTION_REVIEW');
  assert.match(r.caveat, /Structural gate only/);
});
test('missing evidence fails closed', () => {
  assert.equal(evaluatePromotionEvidence(null).eligible, false);
});
test('current pull request head must equal candidate SHA', () => blocked(x => { x.pullRequest.headSha = 'b'.repeat(40); }));
test('pull request from another repository blocks', () => blocked(x => { x.pullRequest.headRepository = 'attacker/fork'; }));
test('closed pull request blocks', () => blocked(x => { x.pullRequest.state = 'closed'; }));
test('invalid pull request number blocks', () => blocked(x => { x.pullRequest.number = 0; }));
test('current pull request head must equal candidate SHA', () => blocked(x => { x.pullRequest.headSha = 'b'.repeat(40); }));
test('pull request head repository mismatch blocks', () => blocked(x => { x.pullRequest.headRepository = 'other/repository'; }));
test('closed pull request blocks', () => blocked(x => { x.pullRequest.state = 'closed'; }));
test('invalid pull request number blocks', () => blocked(x => { x.pullRequest.number = 0; }));
test('candidate SHA mismatch with hosted run blocks', () => blocked(x => { x.run.headSha = 'b'.repeat(40); }));
test('candidate SHA mismatch with receipt blocks', () => blocked(x => { x.receipt.commit = 'b'.repeat(40); }));
test('unknown evidence source blocks', () => blocked(x => { x.run.source = 'local-json'; }));
test('wrong repository blocks', () => blocked(x => { x.run.repository = 'someone/else'; }));
test('wrong workflow path blocks', () => blocked(x => { x.run.workflowPath = '.github/workflows/other.yml'; }));
test('failed hosted run blocks', () => blocked(x => { x.run.conclusion = 'failure'; }));
test('failed job blocks', () => blocked(x => { x.job.conclusion = 'failure'; }));
test('zero runner ID blocks', () => blocked(x => { x.job.runnerId = 0; }));
test('runner name missing blocks', () => blocked(x => { x.job.runnerName = ''; }));
test('job logs missing blocks', () => blocked(x => { x.job.logsUrl = null; }));
test('missing required test step blocks', () => blocked(x => { x.job.steps = x.job.steps.filter(s => s.name !== 'Run the canonical verification script'); }));
test('skipped test step blocks', () => blocked(x => { x.job.steps.find(s => s.name === 'Run the canonical verification script').conclusion = 'skipped'; }));
test('failed receipt suite blocks', () => blocked(x => { x.receipt.python_descent_suite = 'failed'; }));
test('unknown receipt schema blocks', () => blocked(x => { x.receipt.schema = 'v0'; }));
test('receipt run ID mismatch blocks', () => blocked(x => { x.receipt.github_run_id = '111'; }));
test('receipt repository mismatch blocks', () => blocked(x => { x.receipt.github_repository = 'other/repo'; }));
test('missing artifact blocks', () => blocked(x => { x.artifact = null; }));
test('artifact from another run blocks', () => blocked(x => { x.artifact.workflowRunId = 888; }));
test('expired artifact blocks', () => blocked(x => { x.artifact.expired = true; }));
test('all required step names are unique in the contract', () => {
  assert.equal(new Set(REQUIRED_STEPS).size, REQUIRED_STEPS.length);
});
test('gate is not an auto-merge instruction', () => {
  assert.equal(evaluatePromotionEvidence(fixture()).state, 'ELIGIBLE_FOR_PROMOTION_REVIEW');
});

test('failed non-required workflow step also blocks', () => blocked(x => { x.job.steps.push({ name: 'Unexpected diagnostic step', conclusion: 'failure' }); }));
test('duplicate step names block instead of taking last value', () => blocked(x => { x.job.steps.push({ ...x.job.steps[0] }); }));
test('malformed platform step record blocks', () => blocked(x => { x.job.steps.push({ conclusion: 'success' }); }));
test('malformed full commit SHA blocks', () => blocked(x => { x.candidate.sha = 'abc'; }));
test('runner ID missing blocks', () => blocked(x => { delete x.job.runnerId; }));
test('platform run without SHA blocks', () => blocked(x => { delete x.run.headSha; }));


test('evidence envelope rejects getters without invoking them', () => {
  const x = fixture();
  let called = false;
  Object.defineProperty(x, 'candidate', { enumerable: true, configurable: true, get() { called = true; throw new Error('getter executed'); } });
  const result = evaluatePromotionEvidence(x);
  assert.equal(result.eligible, false);
  assert.equal(called, false);
});
test('candidate record rejects unexpected fields', () => blocked(x => { x.candidate.extra = true; }));
test('step records reject accessors without invoking them', () => {
  const x = fixture();
  let called = false;
  const bad = { conclusion: 'success' };
  Object.defineProperty(bad, 'name', { enumerable: true, get() { called = true; throw new Error('getter executed'); } });
  x.job.steps[0] = bad;
  assert.equal(evaluatePromotionEvidence(x).eligible, false);
  assert.equal(called, false);
});
test('steps array rejects custom properties', () => blocked(x => { x.job.steps.note = 'unexpected'; }));
test('artifact expiry must be explicitly false', () => blocked(x => { delete x.artifact.expired; }));


test('CLI with no evidence path exits with usage error', () => {
  const result = spawnSync(process.execPath, ['promotion_gate.js'], { encoding: 'utf8' });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /Usage: node promotion_gate\.js/);
});
test('CLI emits BLOCKED and a nonzero exit for invalid evidence', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'great-scale-gate-'));
  const file = path.join(dir, 'evidence.json');
  try {
    fs.writeFileSync(file, JSON.stringify(null), 'utf8');
    const result = spawnSync(process.execPath, ['promotion_gate.js', file], { encoding: 'utf8' });
    assert.equal(result.status, 1);
    assert.equal(JSON.parse(result.stdout).state, 'BLOCKED');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

console.log(JSON.stringify({ passed, failed, total: passed + failed, results }, null, 2));
if (failed) process.exitCode = 1;
