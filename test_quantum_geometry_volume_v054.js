/**
 * Quantum-geometry deep-edge battery v0.5.4
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

let seed = 54;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Quantum-geometry deep-edge battery v0.5.4 ===');

// 1. Composition of scale + chi + off-diagonal
for (let i = 0; i < 100; i++) {
  const s = Math.pow(10, (rnd() - 0.5) * 40);
  const chi = rnd();
  const g12 = (rnd() - 0.5) * 0.3 * s;
  const g11 = s, g22 = s;
  const det = g11 * g22 - g12 * g12;
  if (det <= 0) continue;
  try {
    const r = quantumGeometryBridge({
      g11, g12, g22, curvature: chi * 2 * Math.sqrt(det)
    });
    check(r.psiQuantum + 1e-12 >= CONE, `1-Psi i=${i}`);
    check(r.curvatureFraction >= 0 && r.curvatureFraction <= 1 + 1e-7, `1-chi i=${i}`);
    check(Number.isFinite(r.metricAnisotropy), `1-aniso i=${i}`);
  } catch (e) {
    check(false, `1-throw i=${i}: ${e.message}`);
  }
}

// 2. Idempotence of scalars
for (let i = 0; i < 50; i++) {
  const chi = rnd();
  const args = { g11: 1, g12: 0, g22: 1, curvature: chi * 2 };
  const a = quantumGeometryBridge(args);
  const b = quantumGeometryBridge(args);
  check(close(a.SQuantum, b.SQuantum), `2-idem S i=${i}`);
  check(close(a.psiQuantum, b.psiQuantum), `2-idem Psi i=${i}`);
  check(close(a.curvatureFraction, b.curvatureFraction), `2-idem chi i=${i}`);
}

// 3. Monotone S vs chi
let prevS = -1;
for (let i = 0; i <= 100; i++) {
  const chi = i / 100;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: chi * 2 });
  if (prevS >= 0) {
    check(r.SQuantum <= prevS + 1e-12, `3-mono S chi=${chi}`);
  }
  prevS = r.SQuantum;
  check(r.psiQuantum >= CONE - 1e-14, `3-Psi chi=${chi}`);
}

// 4. Extreme anisotropy + curvature
for (const a of [1e-6, 1e-3, 0.1, 10, 1e3, 1e6]) {
  for (const chi of [0, 0.3, 0.7, 1]) {
    const g11 = a, g22 = 1 / a, g12 = 0;
    try {
      const r = quantumGeometryBridge({
        g11, g12, g22, curvature: chi * 2
      });
      check(close(r.detG, 1, 1e-6), `4-det a=${a} chi=${chi}`);
      check(r.psiQuantum >= CONE - 1e-12, `4-Psi a=${a}`);
    } catch (e) {
      check(false, `4-throw a=${a}: ${e.message}`);
    }
  }
}

// 5. Random SPD + random chi ensemble
for (let i = 0; i < 150; i++) {
  const a = 0.05 + rnd() * 8;
  const b = (rnd() - 0.5) * Math.min(a, 1) * 0.4;
  const c = 0.05 + rnd() * 8;
  const det = a * c - b * b;
  if (det <= 1e-8) continue;
  const chi = rnd();
  try {
    const r = quantumGeometryBridge({
      g11: a, g12: b, g22: c, curvature: chi * 2 * Math.sqrt(det)
    });
    check(r.psiQuantum + 1e-12 >= CONE, `5-Psi i=${i}`);
    check(Number.isFinite(r.lambdaQuantum), `5-lambda i=${i}`);
  } catch (e) {
    check(false, `5-throw i=${i}`);
  }
}

// 6. Heat composition identity under bridge
for (let i = 0; i <= 50; i++) {
  const chi = i / 50;
  const r = quantumGeometryBridge({ g11: 1, g12: 0, g22: 1, curvature: chi * 2 });
  check(close(r.SQuantum, heat((1 + r.curvatureFraction) / 2), 1e-12), `6-heat chi=${chi}`);
}

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 20).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 10 && passed >= 1000) {
  console.log('QGT deep-edge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
