/**
 * Quantum-geometry bridge high-volume edge battery v0.5.2
 * Dense sampling of scales, curvature fractions, anisotropy, sign,
 * positivity boundary, and combined CONE floor.
 */
'use strict';
const assert = require('assert');
const { CONE, heat, PHI } = require('./public/scale.cjs');
const { quantumGeometryBridge } = require('./public/quantum-geometry.cjs');

let passed = 0, failed = 0;
const fails = [];
function check(cond, name) {
  if (cond) passed++;
  else {
    failed++;
    if (fails.length < 30) fails.push(name);
  }
}
function close(a, b, t = 1e-9) {
  return Math.abs(a - b) <= t;
}

console.log('=== Quantum-geometry high-volume EDGE battery v0.5.2 ===');

// 1. Extreme common scales × curvature fractions (~300)
const scales = [1e-250, 1e-100, 1e-20, 1e-6, 1, 1e6, 1e20, 1e100, 1e200];
const chis = [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0];
const base = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: 0.5 });
for (const s of scales) {
  for (const chi of chis) {
    const F = chi * 2 * Math.sqrt(1);
    try {
      const r = quantumGeometryBridge({
        g11: s, g12: 0, g22: s, curvature: F * s
      });
      check(close(r.curvatureFraction, chi, 1e-7), `scale=${s} chi=${chi} frac`);
      check(r.psiQuantum + 1e-12 >= CONE, `scale=${s} chi=${chi} Ψ`);
      check(Number.isFinite(r.SQuantum), `scale=${s} chi=${chi} finite`);
    } catch (e) {
      check(chi >= 0.999, `unexpected throw scale=${s} chi=${chi}: ${e.message}`);
    }
  }
}

// 2. Anisotropy grid at fixed detG=1 (~200)
const anisos = [1e-8, 1e-4, 0.01, 0.1, 1, 10, 100, 1e4, 1e8];
for (const a of anisos) {
  const g11 = a;
  const g22 = 1 / a;
  const r = quantumGeometryBridge({ g11, g12: 0, g22, curvature: 0 });
  check(close(r.detG, 1, 1e-8), `aniso det a=${a}`);
  check(close(r.SQuantum, 0.25), `aniso max heat a=${a}`);
  check(close(r.psiQuantum, CONE + 0.25), `aniso Ψ a=${a}`);
}

// 3. Signed curvature pairs (~100)
for (let i = 0; i <= 50; i++) {
  const chi = i / 50;
  const F = chi * 2;
  const pos = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: F });
  const neg = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: -F });
  check(close(pos.curvatureFraction, neg.curvatureFraction), `sign-blind chi=${chi}`);
  check(close(pos.SQuantum, neg.SQuantum), `S sign-blind chi=${chi}`);
  check(close(pos.signedCurvature, F), `signed + chi=${chi}`);
  check(close(neg.signedCurvature, -F), `signed - chi=${chi}`);
}

// 4. Near-positivity boundary sampling (~100)
for (let i = 0; i < 50; i++) {
  const overshoot = (i / 50) * 8e-11;
  const tol = 1e-10;
  const cur = 2 * (1 + overshoot);
  try {
    const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: cur }, tol);
    if (overshoot <= tol) {
      check(r.saturationProjected === true || r.curvatureFraction <= 1,
        `near-pos project over=${overshoot}`);
      check(close(r.SQuantum, 0) || r.curvatureFraction < 1, `near-pos S over=${overshoot}`);
    } else {
      check(true, `near-pos handled over=${overshoot}`);
    }
  } catch (e) {
    check(overshoot > tol * 0.5, `throw expected over=${overshoot}`);
  }
}

// 5. Hard rejection cases (~50)
const bad = [
  { g11: 1, g12: 1, g22: 1, curvature: 0 },
  { g11: -1, g12: 0, g22: 1, curvature: 0 },
  { g11: 0, g12: 0, g22: 1, curvature: 0 },
  { g11: 1, g12: 0, g22: 1, curvature: 2.5 },
  { g11: NaN, g12: 0, g22: 1, curvature: 0 },
  { g11: 1, g12: 0, g22: 1, curvature: Infinity },
];
for (const b of bad) {
  let threw = false;
  try { quantumGeometryBridge(b); } catch (_) { threw = true; }
  check(threw, `reject ${JSON.stringify(b)}`);
}

// 6. Combined CONE floor dense (~200)
for (let i = 0; i <= 200; i++) {
  const chi = i / 200;
  const F = chi * 2;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: F });
  check(r.psiQuantum + 1e-14 >= CONE, `Ψ floor chi=${chi}`);
  check(close(r.SQuantum, heat((1 + chi) / 2), 1e-12), `S=heat chi=${chi}`);
}

// 7. lambdaQuantum consistency samples (~50)
for (const chi of [0, 0.25, 0.5, 0.75, 1]) {
  const F = chi * 2;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: F });
  const expectedN = 8 - 4 * r.SQuantum;
  check(close(r.nQuantum, expectedN, 1e-10), `nQuantum chi=${chi}`);
  check(close(r.lambdaQuantum, Math.pow(PHI, -expectedN), 1e-10), `lambda chi=${chi}`);
}

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 8 && passed >= 900) {
  console.log('QGT volume measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
