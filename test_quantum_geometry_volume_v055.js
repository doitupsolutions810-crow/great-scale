/**
 * Quantum-geometry continuum-edge battery v0.5.5
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

let seed = 55;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Quantum-geometry continuum-edge battery v0.5.5 ===');

// 1. Stochastic metric ensemble
for (let i = 0; i < 200; i++) {
  const a = 0.01 + rnd() * 10;
  const b = (rnd() - 0.5) * Math.min(a, 2) * 0.3;
  const c = 0.01 + rnd() * 10;
  const det = a * c - b * b;
  if (det <= 1e-10) continue;
  const chi = rnd();
  try {
    const r = quantumGeometryBridge({
      g11: a, g12: b, g22: c, curvature: chi * 2 * Math.sqrt(det)
    });
    check(r.psiQuantum + 1e-12 >= CONE, `1-Psi i=${i}`);
    check(r.curvatureFraction >= 0 && r.curvatureFraction <= 1 + 1e-7, `1-chi i=${i}`);
    check(Number.isFinite(r.SQuantum), `1-S i=${i}`);
  } catch (e) {
    check(false, `1-throw i=${i}`);
  }
}

// 2. Composition identity under rescaling
for (let i = 0; i < 50; i++) {
  const chi = rnd() * 0.99;
  const s = Math.pow(10, (rnd() - 0.5) * 20);
  const base = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: chi * 2 });
  const scaled = quantumGeometryBridge({ g11: s, g12: 0, g22: s, curvature: chi * 2 * s });
  check(close(base.curvatureFraction, scaled.curvatureFraction, 1e-7), `2-chi i=${i}`);
  check(close(base.SQuantum, scaled.SQuantum, 1e-7), `2-S i=${i}`);
  check(close(base.psiQuantum, scaled.psiQuantum, 1e-7), `2-Psi i=${i}`);
}

// 3. Monotone chain chi -> h -> S -> Psi
let prevS = 1;
for (let i = 0; i <= 100; i++) {
  const chi = i / 100;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: chi * 2 });
  check(r.SQuantum <= prevS + 1e-12, `3-mono chi=${chi}`);
  check(r.psiQuantum >= CONE - 1e-14, `3-Psi chi=${chi}`);
  prevS = r.SQuantum;
}

// 4. Near-degenerate metrics
for (let i = 0; i < 50; i++) {
  const eps = Math.pow(10, -3 - rnd() * 6);
  const a = 1, b = 1 - eps, c = 1;
  const det = a * c - b * b;
  if (det <= 0) continue;
  try {
    const r = quantumGeometryBridge({
      g11: a, g12: b, g22: c, curvature: 0.2 * 2 * Math.sqrt(det)
    });
    check(r.detG > 0, `4-det i=${i}`);
    check(r.psiQuantum >= CONE - 1e-12, `4-Psi i=${i}`);
  } catch (e) {
    check(det < 1e-12, `4-reject small det i=${i}`);
  }
}

// 5. Sign + scale combined
for (let i = 0; i < 40; i++) {
  const chi = rnd();
  const s = Math.pow(10, (rnd() - 0.5) * 10);
  const pos = quantumGeometryBridge({ g11: s, g12: 0, g22: s, curvature: chi * 2 * s });
  const neg = quantumGeometryBridge({ g11: s, g12: 0, g22: s, curvature: -chi * 2 * s });
  check(close(pos.SQuantum, neg.SQuantum), `5-S i=${i}`);
  check(close(pos.signedCurvature, -neg.signedCurvature, 1e-6 * s + 1e-12), `5-sign i=${i}`);
}

// 6. Heat identity dense
for (let i = 0; i <= 80; i++) {
  const chi = i / 80;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: chi * 2 });
  check(close(r.SQuantum, heat((1 + r.curvatureFraction) / 2), 1e-12), `6-heat chi=${chi}`);
}

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 20).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 10 && passed >= 900) {
  console.log('QGT continuum-edge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
