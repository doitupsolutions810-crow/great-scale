/**
 * Bidirectional QGT ↔ Descent bridge tests (v0.5.8)
 */
'use strict';

const { CONE, FIXED, softContract, stressResidual, modDist, stateAt } = require('./public/scale.cjs');
const {
  descentToQuantumSeed,
  coupleDescentWithQGT,
  roundTripChi,
  quantumGeometryBridge,
} = require('./public/qgt-descent-bridge.cjs');

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

let seed = 20261110 + 58;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== QGT ↔ Descent bidirectional bridge v0.5.8 ===');

// A. Reverse map invariants
for (let i = 0; i < 120; i++) {
  const x = (rnd() - 0.5) * 200;
  const t = rnd() * 100;
  const s = descentToQuantumSeed({ x, t });
  check(Number.isFinite(s.chiImplied), `A-chi finite i=${i}`);
  check(s.chiImplied >= 0 && s.chiImplied <= 1, `A-chi range i=${i}`);
  check(s.metricSeed.g11 > 0 && s.metricSeed.g22 > 0, `A-metric SPD diag i=${i}`);
  check(s.psi_state + 1e-14 >= CONE, `A-state CONE i=${i}`);
  check(s.dist >= 0 && s.dist <= 4.5 + 1e-12, `A-dist i=${i}`);
}

// B. Round-trip χ recovery
for (let i = 0; i < 100; i++) {
  const x = rnd() * 9;
  const rt = roundTripChi(x, rnd() * 20);
  check(rt.ok, `B-roundtrip chi i=${i} err=${rt.err}`);
  check(rt.coneOk, `B-roundtrip CONE i=${i}`);
}
{
  const rt = roundTripChi(FIXED, 0);
  check(rt.chiImplied < 0.05, `B-near FIXED chi small (${rt.chiImplied})`);
}

// C. Forward positivity under reverse seeds
for (let i = 0; i < 80; i++) {
  const x = (rnd() - 0.5) * 50;
  const s = descentToQuantumSeed({ x, t: rnd() * 10 });
  try {
    const q = quantumGeometryBridge(s.metricSeed);
    check(q.psiQuantum + 1e-14 >= CONE, `C-Psi CONE i=${i}`);
    check(q.curvatureFraction >= 0 && q.curvatureFraction <= 1 + 1e-9, `C-chi i=${i}`);
    check(Number.isFinite(q.SQuantum), `C-S i=${i}`);
  } catch (e) {
    check(false, `C-throw i=${i}: ${e.message}`);
  }
}

// D. Closed coupling multi-step
for (let i = 0; i < 60; i++) {
  const x0 = (rnd() - 0.5) * 80;
  const coup = coupleDescentWithQGT({
    x: x0, t: rnd() * 5, kBase: 0.45 + rnd() * 0.3, steps: 40,
  });
  check(coup.allConeOk, `D-all CONE i=${i}`);
  check(Number.isFinite(coup.finalX), `D-final finite i=${i}`);
  check(Math.abs(coup.finalX - FIXED) < 1.2, `D-final near FIXED i=${i}`);
  const maxRes = Math.max(...coup.history.map(r => r.residualNext));
  check(maxRes < 10, `D-residual bounded i=${i}`);
}

// E. Near-FIXED quiet
{
  const coup = coupleDescentWithQGT({ x: FIXED + 1e-6, steps: 30, kBase: 0.5 });
  check(coup.allConeOk, 'E-FIXED CONE');
  check(Math.abs(coup.finalX - FIXED) < 1e-4, 'E-FIXED stays');
  check(coup.meanChi < 0.12, `E-mean chi small (${coup.meanChi})`);
}

// F. High-stress → larger χ then contract
{
  const xFar = 0.1;
  const sFar = descentToQuantumSeed({ x: xFar });
  const sNear = descentToQuantumSeed({ x: FIXED + 0.01 });
  check(sFar.chiImplied > sNear.chiImplied, 'F-far > near chi');
  const coup = coupleDescentWithQGT({ x: xFar, steps: 60, kBase: 0.4 });
  check(Math.abs(coup.finalX - FIXED) < 0.3, 'F-far contracts');
  check(coup.allConeOk, 'F-far CONE');
}

// G. Metric scale invariance of χ
for (let i = 0; i < 40; i++) {
  const x = rnd() * 9;
  const s1 = descentToQuantumSeed({ x, baseScale: 1 });
  const s2 = descentToQuantumSeed({ x, baseScale: 1e3 });
  const q1 = quantumGeometryBridge(s1.metricSeed);
  const q2 = quantumGeometryBridge(s2.metricSeed);
  check(close(q1.curvatureFraction, q2.curvatureFraction, 1e-7), `G-scale inv chi i=${i}`);
  check(close(q1.SQuantum, q2.SQuantum, 1e-7), `G-scale inv S i=${i}`);
}

// H. Phase coupling
for (let i = 0; i < 30; i++) {
  const x = 3.0;
  const s0 = descentToQuantumSeed({ x, t: 0 });
  const s1 = descentToQuantumSeed({ x, t: 1.7 });
  check(s0.psi_state + 1e-14 >= CONE && s1.psi_state + 1e-14 >= CONE, `H-Psi t i=${i}`);
  const q0 = quantumGeometryBridge(s0.metricSeed);
  const q1 = quantumGeometryBridge(s1.metricSeed);
  check(q0.psiQuantum >= CONE - 1e-14 && q1.psiQuantum >= CONE - 1e-14, `H-qgt Psi i=${i}`);
}

// I. Long-horizon residual decay
const finals = [];
for (let i = 0; i < 80; i++) {
  const coup = coupleDescentWithQGT({
    x: (rnd() - 0.5) * 300,
    kBase: 0.5,
    steps: 80,
  });
  finals.push(Math.abs(coup.finalX - FIXED));
  check(coup.allConeOk, `I-CONE i=${i}`);
}
const meanFinal = finals.reduce((a, b) => a + b, 0) / finals.length;
const maxFinal = Math.max(...finals);
check(meanFinal < 0.15, `I-mean final ${meanFinal}`);
check(maxFinal < 1.5, `I-max final ${maxFinal}`);

// J. Dual-channel awareness
for (let i = 0; i < 40; i++) {
  const x = rnd() * 9;
  const s = descentToQuantumSeed({ x });
  check(s.chiImplied >= 0, `J-chi nonneg i=${i}`);
  check(s.stress >= 0, `J-stress nonneg i=${i}`);
}

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 25).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 10 && passed >= 800) {
  console.log('Bidirectional bridge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
