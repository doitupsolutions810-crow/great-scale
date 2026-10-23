'use strict';
const assert = require('node:assert/strict');
const { CONE } = require('./public/scale.cjs');
const { quantumGeometryBridge } = require('./public/quantum-geometry.cjs');
const { qiWuZhangChernNumber, qiWuZhangLocalQGT, qiWuZhangGlobalGeometry } = require('./research/topological-qgt.cjs');
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

testCase('signed local curvature integral agrees with the FHS Chern orientation', () => {
  for (const m of [-1, 1]) {
    const d = qiWuZhangGlobalGeometry(m, 40);
    assert.ok(Math.sign(d.integratedCurvature) === Math.sign(d.chernNumber), 'curvature integral and FHS Chern sign must agree');
    assert.ok(Math.abs(d.integratedCurvature - d.chernNumber) < 0.1, '40x40 quadrature error should remain bounded; refine for tighter accuracy');
  }
});
testCase('metric-area budget obeys the Chern lower bound and maps into Great Scale', () => {
  for (const m of [-1, 1]) {
    const d = qiWuZhangGlobalGeometry(m, 40);
    assert.ok(d.metricAreaBudget >= Math.abs(d.chernNumber) - 1e-9);
    close(d.metricAreaBudget, d.absoluteCurvatureBudget, 1e-8);
    assert.ok(d.metricAreaExcess > 0);
    assert.ok(d.topologicalSaturation >= 0 && d.topologicalSaturation <= 1);
    close(d.psiTopological, CONE + d.STopological, 1e-12);
  }
  const trivial = qiWuZhangGlobalGeometry(3, 40);
  close(trivial.chernNumber, 0);
  close(trivial.topologicalSaturation, 0);
  close(trivial.STopological, 0.25);
  close(trivial.psiTopological, CONE + 0.25);
  assert.ok(trivial.metricAreaBudget > 0);
});
testCase('global metric-area budget converges under grid refinement', () => {
  close(qiWuZhangGlobalGeometry(-1, 40).metricAreaBudget, qiWuZhangGlobalGeometry(-1, 80).metricAreaBudget, 2e-4);
  close(qiWuZhangGlobalGeometry(1, 40).metricAreaBudget, qiWuZhangGlobalGeometry(1, 80).metricAreaBudget, 2e-4);
});
testCase('Chern invariant is stable across a phase sweep away from gap closings', () => {
  const sweep = [
    [-3, 0], [-2.5, 0], [-1.5, -1], [-1, -1], [-0.5, -1],
    [0.5, 1], [1, 1], [1.5, 1], [2.5, 0], [3, 0]
  ];
  for (const [m, expected] of sweep) {
    const raw = qiWuZhangChernNumber(m, 40);
    close(Math.round(raw), expected, 1e-8);
    close(raw, Math.round(raw), 1e-5);
  }
});
testCase('curvature quadrature converges across refinement for phases away from transitions', () => {
  for (const m of [-1, 1, 3]) {
    const coarse = qiWuZhangGlobalGeometry(m, 40).integratedCurvature;
    const fine = qiWuZhangGlobalGeometry(m, 80).integratedCurvature;
    assert.ok(Math.abs(fine - Math.round(fine)) <= Math.abs(coarse - Math.round(coarse)) + 1e-9,
      'refined quadrature should not worsen the error at m=' + m);
  }
});

console.log(`topological QGT tests: ${passed} passed, 0 failed`);
