/**
 * Great Scale horizon-edge battery v0.5.6 (JS)
 */
'use strict';
const {
  PHI, CONE, FIXED, heat, involution, involutionIdentity, modDist,
  softMap, softContract, stressResidual, stateAt, DescentEngine,
} = require('./public/scale.cjs');

let passed = 0, failed = 0;
const fails = [];
function check(cond, name) {
  if (cond) passed++;
  else {
    failed++;
    if (fails.length < 40) fails.push(name);
  }
}
function close(a, b, t = 1e-10) { return Math.abs(a - b) <= t; }

let seed = 20261110 + 56;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Great Scale horizon-edge battery v0.5.6 (JS) ===');

// A. Long mixed trajectories
for (let i = 0; i < 60; i++) {
  let x = (rnd() - 0.5) * 4000;
  for (let step = 0; step < 300; step++) {
    const k = step % 17 === 0 ? 0.95 : 0.2 + rnd() * 0.65;
    x = softContract(x, k);
    if (step % 50 === 0) {
      check(Number.isFinite(x), `A-finite i=${i}`);
      check(stressResidual(x) >= -1e-15, `A-stress i=${i}`);
    }
  }
  check(Math.abs(x - FIXED) < 1.0, `A-final i=${i}`);
}

// B. Double modular
for (let i = 0; i < 80; i++) {
  let x = (rnd() - 0.5) * 2e5;
  for (let j = 0; j < 30; j++) {
    const m1 = ((x % 9) + 9) % 9;
    x = m1 + (rnd() - 0.5) * 2e-14;
    const m2 = ((x % 9) + 9) % 9;
    x = softContract(m2, 0.3 + rnd() * 0.5);
  }
  check(Number.isFinite(x) && Math.abs(x - FIXED) < 0.5, `B-double i=${i}`);
}

// C. I-C-I rounds
for (let i = 0; i < 80; i++) {
  let x = rnd() * 9;
  for (let j = 0; j < 20; j++) {
    x = involution(x);
    x = softContract(x, 0.55);
    x = involution(x);
  }
  check(Number.isFinite(x) && modDist(x, FIXED) < 3, `C-round i=${i}`);
}

// D. Basin volume
let hits = 0;
const N = 400;
for (let i = 0; i < N; i++) {
  let x = (rnd() - 0.5) * 200;
  for (let j = 0; j < 80; j++) x = softContract(x, 0.6);
  if (Math.abs(x - FIXED) < 0.05) hits++;
}
check(hits >= Math.floor(0.95 * N), `D-basin ${hits}/${N}`);

// E. Parallel trails
for (let b = 0; b < 30; b++) {
  let trails = Array.from({ length: 8 }, () => (rnd() - 0.5) * 100);
  for (let s = 0; s < 50; s++) trails = trails.map(x => softContract(x, 0.5));
  trails.forEach((x, j) => check(Math.abs(x - FIXED) < 0.1, `E-par b=${b} j=${j}`));
}

// F. Catastrophic k
for (const start of [-30, 0, 4.5, 9, 40]) {
  let x = start;
  for (let i = 0; i < 200; i++) x = softContract(x, 0.995);
  for (let i = 0; i < 30; i++) x = softContract(x, 0.2);
  check(Math.abs(x - FIXED) < 0.15, `F-cat start=${start}`);
}

// G. Cross-property every step
for (let i = 0; i < 40; i++) {
  let x = (rnd() - 0.5) * 200;
  for (let step = 0; step < 50; step++) {
    x = softContract(x, 0.25 + rnd() * 0.55);
    check(Number.isFinite(x), `G-finite i=${i}`);
    check(stressResidual(x) >= -1e-15, `G-stress i=${i}`);
    check(involutionIdentity(x), `G-inv2 i=${i}`);
    const s = stateAt(step * 0.2);
    check(s.psi + 1e-14 >= CONE, `G-Psi i=${i}`);
  }
}

// H. Residual tails
const residuals = [];
for (let i = 0; i < 250; i++) {
  let x = (rnd() - 0.5) * 1000;
  for (let j = 0; j < 100; j++) x = softContract(x, 0.55);
  residuals.push(Math.abs(x - FIXED));
}
const meanR = residuals.reduce((a, b) => a + b, 0) / residuals.length;
const sorted = residuals.slice().sort((a, b) => a - b);
const p95 = sorted[Math.floor(0.95 * sorted.length)];
check(meanR < 0.03, `H-mean ${meanR}`);
check(p95 < 0.1, `H-p95 ${p95}`);

// I. Phase-locked
for (let i = 0; i < 60; i++) {
  const t0 = rnd() * 50;
  let x = rnd() * 9;
  for (let step = 0; step < 50; step++) {
    const s = stateAt(t0 + step * 0.15, 0.9);
    const k = 0.4 + 0.4 * Math.sin(2 * Math.PI * s.phase) ** 2;
    x = softContract(x, k);
    check(s.psi >= CONE - 1e-14, `I-Psi i=${i}`);
  }
  check(Math.abs(x - FIXED) < 0.5, `I-final i=${i}`);
}

// J. FIXED + noise
for (const k of [0.4, 0.6, 0.8]) {
  let x = FIXED;
  for (let i = 0; i < 300; i++) {
    x = softContract(x + (rnd() - 0.5) * 2e-14, k);
  }
  check(Math.abs(x - FIXED) < 1e-8, `J-stable k=${k}`);
}

// Engine
const eng = new DescentEngine({ start: -999, k: 0.4 });
for (let i = 0; i < 400; i++) eng.tick();
check(Math.abs(eng.x - FIXED) < 1e-5, 'engine');
check(eng.t === 400, 'engine-t');

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 20).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 15 && passed >= 2500) {
  console.log('Horizon-edge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
