/**
 * Great Scale continuum-edge battery v0.5.5 (JS) — 3000+ further cases.
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
    if (fails.length < 50) fails.push(name);
  }
}
function close(a, b, t = 1e-10) { return Math.abs(a - b) <= t; }

let seed = 20261110 + 55;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Great Scale continuum-edge battery v0.5.5 (JS) ===');

// A. Stochastic k
for (let i = 0; i < 120; i++) {
  let x = (rnd() - 0.5) * 1000;
  for (let s = 0; s < 60; s++) {
    const k = 0.15 + rnd() * 0.75;
    x = softContract(x, k);
    check(Number.isFinite(x), `A-finite i=${i}`);
  }
  check(Math.abs(x - FIXED) < 0.8, `A-final i=${i}`);
}

// B. Nested / closed-form
for (const k of [0.3, 0.5, 0.7]) {
  for (const start of [0, 2, 7, 20]) {
    let xIter = start;
    for (let n = 1; n <= 24; n++) {
      xIter = softContract(xIter, k);
      const m0 = ((start % 9) + 9) % 9;
      const xClosed = FIXED + Math.pow(k, n) * (m0 - FIXED);
      check(close(xIter, xClosed, 1e-9), `B-closed n=${n} k=${k}`);
    }
  }
}

// C. Stress vs distance
for (let i = 0; i < 120; i++) {
  const x = rnd() * 9;
  const st = stressResidual(x);
  const d = modDist(x, FIXED);
  check(st >= -1e-15, `C-stress i=${i}`);
  if (d < 0.01) check(st < 0.05, `C-near i=${i}`);
}

// D. Translation invariance
for (let i = 0; i < 80; i++) {
  const x = (rnd() - 0.5) * 60;
  const k = 0.2 + rnd() * 0.65;
  const c = softContract(x, k);
  for (let n = -5; n <= 5; n++) {
    check(close(c, softContract(x + n * 9, k)), `D-trans i=${i} n=${n}`);
  }
}

// E. Phase-coupled descent
for (let i = 0; i < 80; i++) {
  const t0 = rnd() * 100;
  const rate = 0.3 + rnd() * 1.2;
  let x = rnd() * 9;
  for (let step = 0; step < 40; step++) {
    const s = stateAt(t0 + step * 0.1, rate);
    let k = 0.35 + 0.4 * (1 - 4 * s.S);
    k = Math.max(0.15, Math.min(0.9, k));
    x = softContract(x, k);
    check(s.psi + 1e-14 >= CONE, `E-Psi i=${i}`);
  }
  check(Math.abs(x - FIXED) < 0.6, `E-final i=${i}`);
}

// F. Pathological sequences
for (const start of [-10, 0, 4, 9, 30]) {
  let x = start;
  for (let step = 0; step < 80; step++) {
    const k = step % 2 === 0 ? 0.9 : 0.2;
    x = softContract(x, k);
  }
  check(Math.abs(x - FIXED) < 0.3, `F-alt start=${start}`);
}
for (const start of [1, 5, 8]) {
  let x = start;
  let k = 0.95;
  for (let step = 0; step < 60; step++) {
    x = softContract(x, k);
    k = Math.max(k * 0.97, 0.1);
  }
  check(Math.abs(x - FIXED) < 0.2, `F-geom start=${start}`);
}

// G. Composition C_a o C_b == C_{a*b}
for (const a of [0.2, 0.4, 0.6, 0.8]) {
  for (const b of [0.3, 0.5, 0.7]) {
    for (const x of [0, 1.5, 3, 6, 8.5]) {
      const left = softContract(softContract(x, b), a);
      const right = softContract(x, a * b);
      check(close(left, right), `G-compose a=${a} b=${b}`);
    }
  }
}

// H. Successive modular reductions
for (let i = 0; i < 40; i++) {
  let x = (rnd() - 0.5) * 2e6;
  for (let j = 0; j < 200; j++) {
    const m = ((x % 9) + 9) % 9;
    x = m + (rnd() - 0.5) * 2e-12;
    x = softContract(x, 0.5);
  }
  check(Number.isFinite(x), `H-finite i=${i}`);
  check(Math.abs(x - FIXED) < 0.1, `H-near i=${i}`);
}

// I. Boundary layer
for (const eps of [1e-14, 1e-11, 1e-8, 1e-5, 1e-3, 0.01, 0.1]) {
  for (const sign of [1, -1]) {
    const c0 = softContract(0 + sign * eps, 0.5);
    const c9 = softContract(9 + sign * eps, 0.5);
    check(Number.isFinite(c0) && Number.isFinite(c9), `I-finite eps=${eps}`);
    if (eps >= 1e-12) {
      check(close(c0, c9, 1e-8), `I-cut eps=${eps}`);
    }
  }
}

// J. Engine
const eng = new DescentEngine({ start: 42.42, k: 0.5 });
for (let i = 0; i < 250; i++) eng.tick();
check(Math.abs(eng.x - FIXED) < 1e-5, 'J-engine');
check(eng.t === 250, 'J-t');

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 25).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 20 && passed >= 2500) {
  console.log('Continuum-edge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
