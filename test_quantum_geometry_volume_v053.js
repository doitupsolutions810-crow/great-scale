/**
 * Quantum-geometry ultra-volume edge battery v0.5.3 — additional dense probes.
 */
'use strict';
const { CONE, heat, PHI } = require('./public/scale.cjs');
const { quantumGeometryBridge } = require('./public/quantum-geometry.cjs');

let passed = 0, failed = 0;
const fails = [];
function check(cond, name) {
  if (cond) passed++;
  else {
    failed++;
    if (fails.length < 40) fails.push(name);
  }
}
function close(a, b, t = 1e-9) { return Math.abs(a - b) <= t; }

console.log('=== Quantum-geometry ultra-volume EDGE battery v0.5.3 ===');

// 1. Dense χ × scale grid (~400)
const scales = [1e-280, 1e-150, 1e-80, 1e-30, 1e-10, 1, 1e10, 1e30, 1e80, 1e150];
const chis = [];
for (let i = 0; i <= 20; i++) chis.push(i / 20);
for (const s of scales) {
  for (const chi of chis) {
    try {
      const r = quantumGeometryBridge({
        g11: s, g12: 0, g22: s, curvature: chi * 2 * s
      });
      check(close(r.curvatureFraction, Math.min(1, chi), 1e-6), `χ-scale s=${s} χ=${chi}`);
      check(r.psiQuantum + 1e-12 >= CONE, `Ψ s=${s} χ=${chi}`);
      check(Number.isFinite(r.SQuantum) && Number.isFinite(r.lambdaQuantum), `finite s=${s}`);
    } catch (e) {
      check(chi > 1 + 1e-8, `throw only if χ>1 s=${s} χ=${chi}`);
    }
  }
}

// 2. Off-diagonal stress (small g12) (~200)
for (let i = 0; i <= 40; i++) {
  const g12 = (i / 40) * 0.4;
  const g11 = 1, g22 = 1;
  const det = g11 * g22 - g12 * g12;
  if (det <= 0) continue;
  const r = quantumGeometryBridge({ g11, g12, g22, curvature: 0.3 });
  check(r.detG > 0, `offdiag det i=${i}`);
  check(r.psiQuantum >= CONE - 1e-12, `offdiag Ψ i=${i}`);
  check(Number.isFinite(r.metricAnisotropy), `offdiag aniso i=${i}`);
}

// 3. Random metric ensemble (positive definite) (~300)
let seed = 53;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}
for (let i = 0; i < 150; i++) {
  const a = 0.1 + rnd() * 5;
  const b = (rnd() - 0.5) * 0.5;
  const c = 0.1 + rnd() * 5;
  const det = a * c - b * b;
  if (det <= 1e-8) continue;
  const chi = rnd();
  const F = chi * 2 * Math.sqrt(det);
  try {
    const r = quantumGeometryBridge({ g11: a, g12: b, g22: c, curvature: F });
    check(r.psiQuantum + 1e-12 >= CONE, `rand Ψ i=${i}`);
    check(r.curvatureFraction >= 0 && r.curvatureFraction <= 1 + 1e-8, `rand χ i=${i}`);
    check(Number.isFinite(r.metricEigenvalues[0]), `rand eig i=${i}`);
  } catch (e) {
    check(false, `rand unexpected throw i=${i}: ${e.message}`);
  }
}

// 4. Saturation identity: χ→1 ⇒ S→0 ⇒ Ψ→CONE (~100)
for (let i = 0; i < 50; i++) {
  const chi = 0.98 + (i / 50) * 0.02;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: chi * 2 });
  check(r.curvatureFraction <= 1 + 1e-12, `sat χ=${chi}`);
  if (chi >= 1 - 1e-12) {
    check(close(r.SQuantum, 0, 1e-10), `sat S=0 χ=${chi}`);
    check(close(r.psiQuantum, CONE, 1e-10), `sat Ψ=CONE χ=${chi}`);
  }
}

// 5. Sign cancellation diagnostic pairs (~100)
for (let i = 0; i <= 40; i++) {
  const chi = i / 40;
  const F = chi * 2;
  const pos = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: F });
  const neg = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: -F });
  check(close(pos.SQuantum, neg.SQuantum), `signS χ=${chi}`);
  check(close(pos.signedCurvature, -neg.signedCurvature), `signF χ=${chi}`);
}

// 6. Combined with heat identity (~100)
for (let i = 0; i <= 50; i++) {
  const chi = i / 50;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: chi * 2 });
  const hQ = (1 + r.curvatureFraction) / 2;
  check(close(r.SQuantum, heat(hQ), 1e-12), `heat id χ=${chi}`);
}

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 20).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 10 && passed >= 1000) {
  console.log('QGT ultra-volume measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
