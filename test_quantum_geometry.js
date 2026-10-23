const assert = require('assert');
const { CONE, heat } = require('./public/scale.cjs');
const { quantumGeometryBridge } = require('./public/quantum-geometry.cjs');
let passed = 0, failed = 0;
function test(name, fn) {
  try { fn(); passed++; console.log('  PASS  ' + name); }
  catch (error) { failed++; console.log('  FAIL  ' + name + ' — ' + error.message); }
}
function close(actual, expected, tol = 1e-10) { assert.ok(Math.abs(actual - expected) <= tol, actual + ' != ' + expected); }
test('zero curvature maps to maximum Great Scale heat', () => {
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 0 });
  close(r.curvatureFraction, 0); close(r.hQuantum, 0.5); close(r.SQuantum, 0.25);
  close(r.SQuantum, heat(r.hQuantum)); close(r.relativeResidual, 1); close(r.psiQuantum, CONE + 0.25);
});
test('saturation maps to zero geometric heat and cone floor', () => {
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 2 });
  close(r.curvatureFraction, 1); close(r.hQuantum, 1); close(r.SQuantum, 0);
  close(r.relativeResidual, 0); close(r.detQ, 0); close(r.psiQuantum, CONE);
});
test('intermediate curvature obeys exact residual-to-heat mapping', () => {
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 1 });
  close(r.curvatureFraction, 0.5); close(r.detQ, 0.75); close(r.relativeResidual, 0.75);
  close(r.SQuantum, 0.1875); close(r.SQuantum, r.relativeResidual / 4); close(r.psiQuantum, CONE + r.SQuantum);
});
test('normalized mapping is invariant under common metric/curvature scaling', () => {
  const a = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 1 });
  const b = quantumGeometryBridge({ g11: 4, g12: 0, g22: 4, curvature: 4 });
  close(a.curvatureFraction, b.curvatureFraction); close(a.SQuantum, b.SQuantum);
});
test('rejects curvature that violates QGT positivity', () => {
  assert.throws(() => quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 2.01 }), /QGT positivity violated/);
});
test('rejects degenerate metric directions', () => {
  assert.throws(() => quantumGeometryBridge({ g11: 1, g12: 1, g22: 1, curvature: 0 }), /positive and nondegenerate/);
});
console.log('\nquantum geometry bridge tests: ' + passed + ' passed, ' + failed + ' failed');
process.exit(failed ? 1 : 0);
