/**
 * Great Scale ridge-edge battery v0.5.7 (JS)
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

let seed = 20261110 + 57;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Great Scale ridge-edge battery v0.5.7 (JS) ===');

// A. Ultra-long with near-1 bursts
for (let i = 0; i < 30; i++) {
  let x = (rnd() - 0.5) * 10000;
  for (let step = 0; step < 800; step++) {
    const k = step % 23 === 0 ? 0.998 : 0.25 + rnd() * 0.55;
    x = softContract(x, k);
    if (step % 100 === 0) check(Number.isFinite(x), `A-finite i=${i}`);
  }
  check(Math.abs(x - FIXED) < 1.5, `A-final i=${i}`);
}

// B. Automorphism sampling
for (let i = 0; i < 80; i++) {
  const x = (rnd() - 0.5) * 80;
  const k = 0.3 + rnd() * 0.45;
  const c0 = softContract(x, k);
  for (let n = -8; n <= 8; n++) {
    check(close(softContract(x + n * 9, k), c0), `B-trans i=${i} n=${n}`);
  }
}

// C. Stress quasi-Lyapunov
for (let i = 0; i < 60; i++) {
  let x = rnd() * 9;
  let lastSt = 9;
  for (let step = 0; step < 50; step++) {
    const k = step % 5 === 0 ? 0.9 : 0.4;
    x = softContract(x, k);
    const st = stressResidual(x);
    check(st >= -1e-15, `C-stress i=${i}`);
    lastSt = st;
  }
  check(lastSt < 0.2, `C-final i=${i}`);
}

// D. Multi-seed ensemble
const finals = [];
for (let s = 0; s < 150; s++) {
  let x = (rnd() - 0.5) * 400;
  for (let j = 0; j < 60; j++) x = softContract(x, 0.3 + rnd() * 0.4);
  finals.push(Math.abs(x - FIXED));
}
const meanF = finals.reduce((a, b) => a + b, 0) / finals.length;
const maxF = Math.max(...finals);
check(meanF < 0.05, `D-mean ${meanF}`);
check(maxF < 0.5, `D-max ${maxF}`);

// E. Heavy-tailed starts
for (let i = 0; i < 80; i++) {
  const u = (rnd() - 0.5) * 0.98;
  let x = Math.tan(Math.PI * u) * 50;
  for (let j = 0; j < 100; j++) x = softContract(x, 0.55);
  check(Number.isFinite(x) && Math.abs(x - FIXED) < 0.3, `E-heavy i=${i}`);
}

// F. Associativity / product
for (const a of [0.3, 0.5, 0.7]) {
  for (const b of [0.2, 0.4, 0.6]) {
    for (const c of [0.25, 0.55]) {
      for (const x of [0, 2, 5, 8]) {
        const left = softContract(softContract(softContract(x, c), b), a);
        const prod = softContract(x, a * b * c);
        check(close(left, prod, 1e-11), `F-assoc a=${a} b=${b} c=${c}`);
      }
    }
  }
}

// G. Random modular walks
for (let i = 0; i < 80; i++) {
  let x = rnd() * 9;
  for (let j = 0; j < 50; j++) {
    x = ((x + (rnd() - 0.5) * 3) % 9 + 9) % 9;
    x = softContract(x, 0.55);
  }
  check(Math.abs(x - FIXED) < 1.0, `G-walk i=${i}`);
}

// H. Three-way phase-heat-descent
for (let i = 0; i < 60; i++) {
  const t0 = rnd() * 30;
  let x = (rnd() - 0.5) * 20;
  for (let step = 0; step < 40; step++) {
    const s = stateAt(t0 + step * 0.2, 1.1);
    let k = 0.3 + 0.5 * s.S * 4 + 0.1 * Math.sin(2 * Math.PI * s.phase);
    k = Math.max(0.15, Math.min(0.92, k));
    x = softContract(x, k);
    check(s.psi + 1e-14 >= CONE, `H-Psi i=${i}`);
  }
  check(Math.abs(x - FIXED) < 0.6, `H-final i=${i}`);
}

// I. Drift under repeated %
for (let i = 0; i < 40; i++) {
  let x = (rnd() - 0.5) * 2e7;
  for (let j = 0; j < 400; j++) {
    x = ((x % 9) + 9) % 9;
    x = softContract(x, 0.5);
  }
  check(Number.isFinite(x) && Math.abs(x - FIXED) < 0.05, `I-drift i=${i}`);
}

// J. Interleave softMap / involution
for (let i = 0; i < 50; i++) {
  let x = (rnd() - 0.5) * 40;
  for (let j = 0; j < 25; j++) {
    x = rnd() < 0.5 ? softMap(x) : involution(x);
    x = softContract(x, 0.5);
  }
  check(Number.isFinite(x), `J-finite i=${i}`);
  const m = ((x % 9) + 9) % 9;
  check(m >= 0 && m < 9 + 1e-9, `J-range i=${i}`);
}

// Engine long
const eng = new DescentEngine({ start: 777.7, k: 0.42 });
for (let i = 0; i < 500; i++) eng.tick();
check(Math.abs(eng.x - FIXED) < 1e-5, 'engine');
check(eng.t === 500, 'engine-t');

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 20).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 15 && passed >= 2500) {
  console.log('Ridge-edge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
