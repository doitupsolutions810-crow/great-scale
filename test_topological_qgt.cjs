'use strict';
const assert = require('node:assert/strict');
const { quantumGeometryBridge } = require('./public/quantum-geometry.cjs');
const { qiWuZhangChernNumber, qiWuZhangLocalQGT } = require('./research/topological-qgt.cjs');
let passed = 0;
function close(a, b, tol = 1e-8) { assert.ok(Math.abs(a - b) <= tol, `${a} != ${b} (tol ${tol})`); }
function testCase(name, fn) { fn(); passed++; console.log('  PASS  ' + name); }
testCase('QWZ lower band has Chern number -1 for m=-1', () => close(qiWuZhangChernNumber(-1), -1));
testCase('QWZ lower band has Chern number +1 for m=+1', () => close(qiWuZhangChernNumber(1), 1));
testCase('QWZ trivial phase m=3 has Chern number 0', () => close(qiWuZhangChernNumber(3), 0));
testCase('all topological phase-boundary masses are rejected even on odd grids', () => {
  for (const m of [-2, 0, 2]) assert.throws(() => qiWuZhangChernNumber(m, 41), /phase boundary/);
});
testCase('local QGT saturates the positivity bound in the m=-1 phase', () => {
  const r = quantumGeometryBridge(qiWuZhangLocalQGT(.37, .81, -1));
  close(r.curvatureFraction, 1, 1e-9); close(r.SQuantum, 0, 1e-9); close(r.psiQuantum, .3819660112501051, 1e-9);
});
testCase('opposite Chern phases share the same local Great Scale floor', () => {
  const a = quantumGeometryBridge(qiWuZhangLocalQGT(.37, .81, -1));
  const b = quantumGeometryBridge(qiWuZhangLocalQGT(.37, .81, 1));
  close(a.SQuantum, 0, 1e-9); close(b.SQuantum, 0, 1e-9); close(a.psiQuantum, b.psiQuantum, 1e-9);
  close(qiWuZhangChernNumber(-1), -qiWuZhangChernNumber(1), 1e-8);
});

testCase('Chern result is stable across 20x20 and 40x40 grids', () => {
  close(qiWuZhangChernNumber(-1, 20), qiWuZhangChernNumber(-1, 40));
  close(qiWuZhangChernNumber(1, 20), qiWuZhangChernNumber(1, 40));
});
testCase('invalid grid sizes and nonfinite masses are rejected', () => {
  assert.throws(() => qiWuZhangChernNumber(1, 3), /gridSize/);
  assert.throws(() => qiWuZhangChernNumber(Number.NaN), /finite/);
});

console.log(`topological QGT tests: ${passed} passed, 0 failed`);
