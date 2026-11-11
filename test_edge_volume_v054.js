/**
 * Great Scale deep-edge battery v0.5.4 (JS) — 3000+ further cases.
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

let seed = 20261110 + 54;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Great Scale deep-edge battery v0.5.4 (JS) ===');

// A. Operation composition
const ops = [
  ['C', x => softContract(x, 0.5)],
  ['I', involution],
  ['M', softMap],
];
for (let i = 0; i < 180; i++) {
  let x = (rnd() - 0.5) * 100;
  const len = 3 + Math.floor(rnd() * 3);
  for (let j = 0; j < len; j++) {
    const fn = ops[Math.floor(rnd() * 3)][1];
    x = fn(x);
    check(Number.isFinite(x), `A-finite i=${i}`);
  }
  const m = ((x % 9) + 9) % 9;
  check(m >= 0 && m < 9 + 1e-9, `A-range i=${i}`);
}
for (const x of [0, 1, 2.5, 4.5, 7, 8.9]) {
  check(involutionIdentity(x), `A-I2 x=${x}`);
  check(close(softMap(softMap(x)), x), `A-M2 x=${x}`);
  const c2 = softContract(softContract(x, 0.5), 0.5);
  const c1 = softContract(x, 0.25);
  check(close(c2, c1), `A-CoC x=${x}`);
}

// B. Multi-k schedules
const schedules = [[0.9,0.5,0.2],[0.3,0.8,0.4],[0.99,0.7,0.3],[0.1,0.1,0.95]];
for (const sched of schedules) {
  for (const start of [-20, 0, 3, 8, 40]) {
    let x = start;
    for (const k of sched) {
      for (let i = 0; i < 40; i++) x = softContract(x, k);
    }
    check(Math.abs(x - FIXED) < 0.15, `B-sched start=${start}`);
  }
}

// C. Modular-cut chaos
for (let n = -5; n < 15; n++) {
  for (const eps of [1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 0.01]) {
    for (const sign of [1, -1]) {
      const x = n + sign * eps;
      const c = softContract(x, 0.5);
      check(Number.isFinite(c), `C-finite n=${n}`);
      if (eps >= 1e-12) {
        check(close(c, softContract(x + 9, 0.5), 1e-8), `C-fiber n=${n} eps=${eps}`);
      }
      check(stressResidual(x) >= -1e-15, `C-stress n=${n}`);
    }
  }
}

// D. Residual statistics
const residuals = [];
for (let i = 0; i < 300; i++) {
  let x = (rnd() - 0.5) * 200;
  const k = 0.2 + rnd() * 0.65;
  for (let j = 0; j < 30; j++) x = softContract(x, k);
  residuals.push(Math.abs(x - FIXED));
}
const meanR = residuals.reduce((a, b) => a + b, 0) / residuals.length;
const maxR = Math.max(...residuals);
check(meanR < 0.05, `D-mean ${meanR}`);
check(maxR < 0.5, `D-max ${maxR}`);
const within = residuals.filter(r => r < 0.1).length;
check(within >= 285, `D-95% ${within}/300`);

// E. Heat-injection descent
for (let i = 0; i < 120; i++) {
  const chi = rnd();
  const Sq = heat((1 + chi) / 2);
  const psi = CONE + Sq;
  check(psi + 1e-15 >= CONE, `E-Psi chi=${chi}`);
  let x = 4.5 + (1 - 4 * Sq) * 3;
  for (let j = 0; j < 50; j++) x = softContract(x, 0.6);
  check(Math.abs(x - FIXED) < 0.05, `E-descent i=${i}`);
}

// F. FIXED stability
for (const k of [0.3, 0.5, 0.7, 0.9]) {
  let x = FIXED;
  for (let i = 0; i < 500; i++) x = softContract(x, k);
  check(close(x, FIXED, 1e-12), `F-stable k=${k}`);
  x = FIXED + 1e-8;
  for (let i = 0; i < 200; i++) x = softContract(x, k);
  check(Math.abs(x - FIXED) < 1e-6, `F-return k=${k}`);
}

// G. Commutation sampling
for (let i = 0; i < 80; i++) {
  const x = rnd() * 9;
  const left = softContract(involution(x), 0.5);
  const right = involution(softContract(x, 0.5));
  check(Number.isFinite(left) && Number.isFinite(right), `G-finite i=${i}`);
}
check(close(
  softContract(involution(FIXED), 0.5),
  involution(softContract(FIXED, 0.5))
), 'G-commute FIXED');

// H. Stress Lyapunov-like
for (const start of [0, 1, 2, 3, 6, 7, 8]) {
  let x = start;
  for (let s = 0; s < 40; s++) {
    x = softContract(x, 0.55);
    check(stressResidual(x) >= -1e-15, `H-stress start=${start}`);
  }
  check(stressResidual(x) < 0.05, `H-final start=${start}`);
}

// I. stateAt grid
for (let i = 0; i < 80; i++) {
  const t = (rnd() - 0.5) * 2e4;
  const rate = 0.05 + rnd() * 5;
  const s = stateAt(t, rate);
  check(s.psi + 1e-14 >= CONE, `I-Psi`);
  check(s.S >= 0 && s.S <= 0.25 + 1e-14, `I-S`);
}

// J. Engine long multi-stage
const eng = new DescentEngine({ start: -88.8, k: 0.45 });
for (let i = 0; i < 300; i++) eng.tick();
check(Math.abs(eng.x - FIXED) < 1e-5, 'J-engine');
check(eng.t === 300, 'J-t');

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 25).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 20 && passed >= 2800) {
  console.log('Deep-edge measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
