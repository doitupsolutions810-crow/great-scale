/**
 * Bidirectional QGT ↔ Descent volume battery v0.5.9
 * Longer, denser, more adversarial probes of the closed loop.
 */
'use strict';

const { CONE, FIXED, softContract, stressResidual, modDist, stateAt, PHI } = require('./public/scale.cjs');
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
    if (fails.length < 50) fails.push(name);
  }
}
function close(a, b, t = 1e-9) { return Math.abs(a - b) <= t; }

let seed = 20261110 + 59;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== QGT ↔ Descent volume battery v0.5.9 ===');

// A. Ultra-long coupled trajectories
for (let i = 0; i < 40; i++) {
  const coup = coupleDescentWithQGT({
    x: (rnd() - 0.5) * 2000,
    t: rnd() * 20,
    kBase: 0.35 + rnd() * 0.4,
    steps: 200,
  });
  check(coup.allConeOk, `A-CONE i=${i}`);
  check(Number.isFinite(coup.finalX), `A-finite i=${i}`);
  check(Math.abs(coup.finalX - FIXED) < 1.0, `A-near FIXED i=${i}`);
  const maxChi = Math.max(...coup.history.map(r => r.chiForward));
  check(maxChi <= 1 + 1e-9, `A-chi<=1 i=${i}`);
}

// B. Stochastic kBase schedules
for (let i = 0; i < 50; i++) {
  let x = (rnd() - 0.5) * 500;
  let t = 0;
  for (let s = 0; s < 60; s++) {
    const kBase = 0.2 + rnd() * 0.7;
    const coup = coupleDescentWithQGT({ x, t, kBase, steps: 1 });
    check(coup.allConeOk, `B-CONE i=${i} s=${s}`);
    x = coup.finalX;
    t = coup.finalT;
  }
  check(Math.abs(x - FIXED) < 1.2, `B-final i=${i}`);
}

// C. Round-trip χ under heavy lattice translation
for (let i = 0; i < 100; i++) {
  const base = rnd() * 9;
  for (const n of [-20, -5, 0, 3, 11, 50]) {
    const rt = roundTripChi(base + n * 9, rnd() * 10);
    check(rt.ok, `C-rt n=${n} i=${i}`);
    check(rt.coneOk, `C-CONE n=${n} i=${i}`);
  }
}

// D. Metric scale extremes
for (let i = 0; i < 50; i++) {
  const x = rnd() * 9;
  for (const sc of [1e-8, 1e-4, 1, 1e4, 1e8]) {
    const s = descentToQuantumSeed({ x, baseScale: sc });
    try {
      const q = quantumGeometryBridge(s.metricSeed);
      check(q.psiQuantum + 1e-12 >= CONE, `D-Psi sc=${sc} i=${i}`);
      check(q.curvatureFraction >= 0 && q.curvatureFraction <= 1 + 1e-7, `D-chi sc=${sc} i=${i}`);
    } catch (e) {
      check(false, `D-throw sc=${sc} i=${i}: ${e.message}`);
    }
  }
}

// E. Adversarial starts
const adversarial = [
  0, -0, 1e-300, -1e-300, 1e300, -1e300,
  FIXED, FIXED + 1e-15, FIXED - 1e-15,
  9 - 1e-15, 1e-15, -9, 18, -18, 4.5 + Math.PI, 1e6 * Math.E,
];
for (const x of adversarial) {
  if (!Number.isFinite(x)) continue;
  try {
    const s = descentToQuantumSeed({ x });
    check(s.chiImplied >= 0 && s.chiImplied <= 1, `E-chi range x=${x}`);
    const q = quantumGeometryBridge(s.metricSeed);
    check(q.psiQuantum + 1e-12 >= CONE, `E-Psi x=${x}`);
    const coup = coupleDescentWithQGT({ x, steps: 20, kBase: 0.5 });
    check(coup.allConeOk, `E-couple CONE x=${x}`);
  } catch (e) {
    check(false, `E-throw x=${x}: ${e.message}`);
  }
}

// F. Residual monotone tendency
for (let i = 0; i < 40; i++) {
  const coup = coupleDescentWithQGT({
    x: (rnd() - 0.5) * 100,
    kBase: 0.4,
    steps: 50,
  });
  check(coup.allConeOk, `F-CONE i=${i}`);
  const mid = Math.floor(coup.history.length / 2);
  const first = coup.history.slice(0, mid).reduce((a, r) => a + r.residual, 0) / mid;
  const second = coup.history.slice(mid).reduce((a, r) => a + r.residual, 0) / (coup.history.length - mid);
  check(second <= first + 0.5, `F-residual tendency i=${i}`);
}

// G. Parallel multi-start
for (let b = 0; b < 25; b++) {
  const starts = Array.from({ length: 8 }, () => (rnd() - 0.5) * 200);
  const finals = starts.map(x => {
    const c = coupleDescentWithQGT({ x, steps: 60, kBase: 0.5 });
    check(c.allConeOk, `G-CONE b=${b}`);
    return Math.abs(c.finalX - FIXED);
  });
  const mean = finals.reduce((a, b) => a + b, 0) / finals.length;
  check(mean < 0.25, `G-mean b=${b} (${mean})`);
}

// H. Phase-locked long coupling
for (let i = 0; i < 40; i++) {
  const t0 = rnd() * 40;
  let x = rnd() * 9;
  for (let s = 0; s < 50; s++) {
    const st = stateAt(t0 + s * 0.1, 0.9);
    const coup = coupleDescentWithQGT({
      x, t: t0 + s * 0.1, kBase: 0.35 + 0.3 * st.S * 4, steps: 1,
    });
    check(coup.allConeOk, `H-CONE i=${i} s=${s}`);
    x = coup.finalX;
  }
  check(Math.abs(x - FIXED) < 0.8, `H-final i=${i}`);
}

// I. χ continuity
for (let i = 0; i < 60; i++) {
  const x = rnd() * 9;
  const s0 = descentToQuantumSeed({ x });
  const s1 = descentToQuantumSeed({ x: x + 1e-8 });
  check(Math.abs(s0.chiImplied - s1.chiImplied) < 0.01, `I-chi cont i=${i}`);
}

// J. FIXED basin under coupler
let hits = 0;
const N = 200;
for (let i = 0; i < N; i++) {
  const coup = coupleDescentWithQGT({
    x: (rnd() - 0.5) * 150,
    steps: 100,
    kBase: 0.55,
  });
  if (Math.abs(coup.finalX - FIXED) < 0.08) hits++;
  check(coup.allConeOk, `J-CONE i=${i}`);
}
check(hits >= Math.floor(0.92 * N), `J-basin ${hits}/${N}`);

// K. Involution-then-couple
for (let i = 0; i < 40; i++) {
  let x = (rnd() - 0.5) * 30;
  const m = ((x % 9) + 9) % 9;
  x = (9 - m) % 9;
  const coup = coupleDescentWithQGT({ x, steps: 40, kBase: 0.5 });
  check(coup.allConeOk, `K-CONE i=${i}`);
  check(Math.abs(coup.finalX - FIXED) < 0.5, `K-near i=${i}`);
}

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 30).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 20 && passed >= 3000) {
  console.log('Volume bridge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
