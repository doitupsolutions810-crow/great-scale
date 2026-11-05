'use strict';
const assert = require('node:assert/strict');
const { assessEvidence } = require('./public/great-scale-evidence.cjs');

const base = {
  topology: { chern: 1, absoluteCurvature: 2 },
  geometry: { status: 'measured' },
  provenance: { commit: 'abc123', inputDigest: 'sha256:demo' },
  execution: { command: 'node test.js', exitCode: 0 }
};
function clone(x) { return JSON.parse(JSON.stringify(x)); }

let passed = 0;
function test(name, fn) { fn(); passed++; console.log('  PASS  ' + name); }

test('valid record preserves separate evidence channels', () => {
  const r = assessEvidence(base);
  assert.equal(r.status, 'recorded-not-scientifically-certified');
  assert.deepEqual(r.issues, []);
  assert.equal(r.derived.eta, 0.5);
  assert.equal(r.derived.S, 0.1875);
});

test('sign reversal preserves scalar but changes signed channel', () => {
  const a = assessEvidence(base);
  const b = assessEvidence({ ...clone(base), topology: { chern: -1, absoluteCurvature: 2 } });
  assert.equal(a.derived.S, b.derived.S);
  assert.equal(a.derived.eta, -b.derived.eta);
});

test('common positive scaling preserves normalized scalar', () => {
  const a = assessEvidence(base);
  const b = assessEvidence({ ...clone(base), topology: { chern: 10, absoluteCurvature: 20 } });
  assert.ok(Math.abs(a.derived.S - b.derived.S) < 1e-12);
});

test('zero curvature budget is explicitly invalid/undefined', () => {
  const r = assessEvidence({ ...clone(base), topology: { chern: 0, absoluteCurvature: 0 } });
  assert.equal(r.status, 'invalid');
  assert.ok(r.issues.some(x => x.includes('undefined')));
  assert.equal(r.derived, null);
});

test('triangle inequality violation is rejected', () => {
  const r = assessEvidence({ ...clone(base), topology: { chern: 2, absoluteCurvature: 1 } });
  assert.equal(r.status, 'invalid');
  assert.ok(r.issues.some(x => x.includes('triangle-inequality')));
});

test('unresolved geometry cannot be marked complete', () => {
  const r = assessEvidence({ ...clone(base), geometry: { status: 'unresolved' } });
  assert.equal(r.status, 'incomplete');
});

test('nonzero execution exit is distinguished from scientific invalidity', () => {
  const r = assessEvidence({ ...clone(base), execution: { command: 'npm test', exitCode: 1 } });
  assert.equal(r.status, 'failed');
  assert.deepEqual(r.issues, []);
});

test('missing provenance and execution evidence is rejected', () => {
  const r = assessEvidence({ topology: base.topology, geometry: base.geometry });
  assert.equal(r.status, 'invalid');
  assert.ok(r.issues.some(x => x.includes('provenance')));
  assert.ok(r.issues.some(x => x.includes('execution')));
});

console.log(`\n${passed}/8 evidence-ledger tests passed.`);
