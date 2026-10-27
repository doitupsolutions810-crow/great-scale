'use strict';
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { verifyExecutionEvidence } = require('./public/great-scale-verification-gate.cjs');
const capturedOutput = 'PASS: npm test';
const digest = 'sha256:' + crypto.createHash('sha256').update(capturedOutput, 'utf8').digest('hex');
const valid = {
  commit: '129ff3a3f3cf39a9563728086203354e05c76d13',
  command: 'npm test',
  exitCode: 0,
  runId: 'local-run-001',
  capturedOutput,
  outputDigest: digest,
  startedAt: '2026-10-25T03:00:00Z'
};
let passed = 0;
function test(name, fn) { fn(); passed++; console.log('  PASS  ' + name); }
test('matching output digest validates record integrity, not scientific truth', () => {
  assert.equal(verifyExecutionEvidence(valid).status, 'record-integrity-valid');
});
test('claimed exit code without run identity is unverified', () => {
  const x = { ...valid }; delete x.runId;
  assert.equal(verifyExecutionEvidence(x).status, 'unverified');
});
test('missing output digest is unverified', () => {
  const x = { ...valid }; delete x.outputDigest;
  assert.equal(verifyExecutionEvidence(x).status, 'unverified');
});
test('digest-shaped value that does not match output is rejected', () => {
  const x = { ...valid, outputDigest: 'sha256:' + 'a'.repeat(64) };
  assert.equal(verifyExecutionEvidence(x).status, 'unverified');
  assert.ok(verifyExecutionEvidence(x).issues.some(issue => issue.includes('does not match')));
});
test('missing captured output is unverified', () => {
  const x = { ...valid }; delete x.capturedOutput;
  assert.equal(verifyExecutionEvidence(x).status, 'unverified');
});
test('nonzero observed exit is preserved as failed execution', () => {
  assert.equal(verifyExecutionEvidence({ ...valid, exitCode: 1 }).status, 'execution-failed');
});
test('malformed commit is rejected', () => {
  assert.equal(verifyExecutionEvidence({ ...valid, commit: 'not-a-sha' }).status, 'unverified');
});
console.log(`\n${passed}/7 verification-gate tests passed.`);
