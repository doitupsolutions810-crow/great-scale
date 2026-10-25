'use strict';
const assert = require('node:assert/strict');
const { verifyExecutionEvidence } = require('./public/great-scale-verification-gate.cjs');
const valid = {
  commit: '129ff3a3f3cf39a9563728086203354e05c76d13',
  command: 'npm test',
  exitCode: 0,
  runId: 'local-run-001',
  outputDigest: 'sha256:' + 'a'.repeat(64),
  startedAt: '2026-10-25T03:00:00Z'
};
let passed = 0;
function test(name, fn) { fn(); passed++; console.log('  PASS  ' + name); }
test('complete run record accepted as execution evidence, not scientific proof', () => {
  assert.equal(verifyExecutionEvidence(valid).status, 'execution-evidence-complete');
});
test('claimed exit code without run identity is unverified', () => {
  const x = { ...valid }; delete x.runId;
  assert.equal(verifyExecutionEvidence(x).status, 'unverified');
});
test('missing output digest is unverified', () => {
  const x = { ...valid }; delete x.outputDigest;
  assert.equal(verifyExecutionEvidence(x).status, 'unverified');
});
test('nonzero observed exit is preserved as failed execution', () => {
  assert.equal(verifyExecutionEvidence({ ...valid, exitCode: 1 }).status, 'execution-failed');
});
test('malformed commit is rejected', () => {
  assert.equal(verifyExecutionEvidence({ ...valid, commit: 'not-a-sha' }).status, 'unverified');
});
console.log(`\n${passed}/5 verification-gate tests passed.`);
