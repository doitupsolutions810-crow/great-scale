/**
 * Quantum-geometry bridge edge battery v0.5.1
 * Extreme scales, near-positivity boundary, anisotropy extremes,
 * signed-curvature cancellation diagnostics, combined with Great Scale state.
 */
'use strict';
const assert = require('assert');
const { CONE, heat, PHI } = require('./public/scale.cjs');
const { quantumGeometryBridge } = require('./public/quantum-geometry.cjs');

let passed = 0, failed = 0;
function test(name, fn) {
  try { fn(); passed++; console.log('  PASS  ' + name); }
  catch (e) { failed++; console.log('  FAIL  ' + name + ' — ' + e.message); }
}
function close(a, b, t = 1e-10) {
  assert.ok(Math.abs(a - b) <= t, `${a} != ${b}`);
}

// --- Extreme common scaling still invariant ---
test('bridge invariant under extreme common positive scales', () => {
  const base = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 0.7 });
  for (const s of [1e-300, 1e-100, 1e-20, 1e20, 1e100, 1e250]) {
    const r = quantumGeometryBridge({
      g11: s, g12: 0, g22: s, curvature: 0.7 * s
    });
    close(r.curvatureFraction, base.curvatureFraction, 1e-9);
    close(r.SQuantum, base.SQuantum, 1e-9);
    assert.ok(r.metricEigenvalues.every(Number.isFinite));
  }
});

// --- Near-positivity boundary with tolerance ---
test('tolerated overshoot still projects to saturation', () => {
  const tol = 1e-10;
  const r = quantumGeometryBridge(
    { g11: 1, g12: 0, g22: 1, curvature: 2 * (1 + 5e-11) },
    tol
  );
  assert.ok(r.rawCurvatureFraction > 1);
  assert.strictEqual(r.saturationProjected, true);
  close(r.curvatureFraction, 1);
  close(r.SQuantum, 0);
  close(r.psiQuantum, CONE);
});

test('hard positivity violation still throws beyond tolerance', () => {
  assert.throws(
    () => quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 2.01 }),
    /QGT positivity violated/
  );
});

// --- Extreme anisotropy ---
test('extreme anisotropy at fixed determinant preserves SQuantum', () => {
  const iso = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 0 });
  const aniso = quantumGeometryBridge({ g11: 1e6, g12: 0, g22: 1e-6, curvature: 0 });
  close(iso.detG, 1);
  close(aniso.detG, 1);
  close(iso.SQuantum, aniso.SQuantum);
  close(iso.SQuantum, 0.25);
  assert.ok(aniso.metricAnisotropy < 1e-11);
});

// --- Signed curvature diagnostics ---
test('signed curvature preserved while scalar heat is sign-blind', () => {
  const pos = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 0.8 });
  const neg = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: -0.8 });
  close(pos.curvatureFraction, neg.curvatureFraction);
  close(pos.SQuantum, neg.SQuantum);
  close(pos.signedCurvature, 0.8);
  close(neg.signedCurvature, -0.8);
});

// --- Degenerate / negative guards ---
test('rejects degenerate, negative, zero-diagonal metrics', () => {
  assert.throws(() => quantumGeometryBridge({ g11: 1, g12: 1, g22: 1, curvature: 0 }),
    /positive and nondegenerate/);
  assert.throws(() => quantumGeometryBridge({ g11: -1, g12: 0, g22: 1, curvature: 0 }),
    /diagonal entries must be positive/);
  assert.throws(() => quantumGeometryBridge({ g11: 0, g12: 0, g22: 1, curvature: 0 }),
    /diagonal entries must be positive/);
});

// --- Non-finite inputs ---
test('rejects non-finite metric or curvature', () => {
  assert.throws(() => quantumGeometryBridge({ g11: NaN, g12: 0, g22: 1, curvature: 0 }));
  assert.throws(() => quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: Infinity }));
  assert.throws(() => quantumGeometryBridge({ g11: 1, g12: 0, g22: -Infinity, curvature: 0 }));
});

// --- Zero curvature family with Bloch-like metric ---
test('qutrit-like zero-curvature retains area and max heat', () => {
  const x = 0.3, y = 0.4;
  const s = 1 + x * x + y * y;
  const g11 = (1 + y * y) / (s * s);
  const g12 = -x * y / (s * s);
  const g22 = (1 + x * x) / (s * s);
  const r = quantumGeometryBridge({ g11, g12, g22, curvature: 0 });
  close(r.relativeResidual, 1);
  close(r.SQuantum, 0.25);
  close(r.psiQuantum, CONE + 0.25);
});

// --- Combined with Great Scale state floor ---
test('bridge Ψ_quantum never below CONE', () => {
  for (const chi of [0, 0.25, 0.5, 0.75, 1.0]) {
    // construct metric+curvature realizing the fraction
    const detG = 1;
    const F = chi * 2 * Math.sqrt(detG);
    const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: F });
    close(r.curvatureFraction, chi, 1e-12);
    assert.ok(r.psiQuantum + 1e-14 >= CONE);
    close(r.SQuantum, heat((1 + chi) / 2));
  }
});

// --- lambdaQuantum consistency ---
test('lambdaQuantum follows φ^{-n} with n = 8-4S', () => {
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 0 });
  close(r.SQuantum, 0.25);
  close(r.nQuantum, 7);
  close(r.lambdaQuantum, Math.pow(PHI, -7), 1e-12);
});

console.log(`\nquantum-geometry EDGE tests: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
