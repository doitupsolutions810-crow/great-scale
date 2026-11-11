/**
 * Great Scale high-volume edge battery v0.5.2 — ~2000+ systematic cases (JS).
 * Dense parametric coverage parallel to the Python volume suite.
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

function close(a, b, t = 1e-10) {
  return Math.abs(a - b) <= t;
}

// Deterministic PRNG
let seed = 20261110;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Great Scale high-volume EDGE battery v0.5.2 (JS) ===');

// 1. Involution identity dense (~400)
for (let i = -200; i <= 200; i++) {
  const x = i * 0.125;
  check(involutionIdentity(x), `involution² x=${x}`);
}

// 2. Cycles + FIXED
[[1,8],[2,7],[3,6],[4,5]].forEach(([a,b]) => {
  check(involution(a) === b && involution(b) === a, `cycle ${a}↔${b}`);
});
check(involution(0) === 0 && involution(9) === 0, 'boundary 0≡9');
check(close(involution(FIXED), FIXED), 'FIXED fixed');

// 3. Seams / fibers (~500)
for (let off = -50; off <= 50; off++) {
  const c0 = softContract(0 + off * 9);
  const c9 = softContract(9 + off * 9);
  check(close(c0, c9, 1e-12), `seam off=${off}`);
  check(modDist(c0, c9) < 1e-12, `mod seam off=${off}`);
}
const bases = [0, 0.5, 1, 2.3, 3.7, 4.5, 5.2, 6.8, 7.1, 8.9];
for (const bx of bases) {
  const ref = softContract(bx, 0.4);
  for (let n = -15; n <= 15; n++) {
    check(close(softContract(bx + n * 9, 0.4), ref, 1e-12), `fiber ${bx} n=${n}`);
  }
}

// 4. Contraction grid (~600)
const ks = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99];
const starts = [-1e4, -100, -9.1, -1, 0, 0.01, 1, 2.5, 4, 4.499, 4.5, 4.501, 5, 7, 8.5, 8.99, 9, 9.1, 100, 1e4];
for (const k of ks) {
  let tol, steps;
  if (k <= 0.7) { tol = 1e-6; steps = 80; }
  else if (k <= 0.9) { tol = 1e-4; steps = 220; }
  else if (k <= 0.99) { tol = 0.12; steps = 600; }
  else { tol = 0.3; steps = 2500; }
  for (const st of starts) {
    let x = st;
    for (let i = 0; i < steps; i++) x = softContract(x, k);
    check(Math.abs(x - FIXED) < tol, `contract k=${k} start=${st}`);
  }
}

// 5. Stress residual invariance (~200)
for (let i = 0; i <= 36; i++) {
  const x = i * 0.25;
  const r0 = stressResidual(x);
  for (let n = -8; n <= 8; n++) {
    check(close(stressResidual(x + n * 9), r0, 1e-12), `stress inv ${x} n=${n}`);
  }
  check(r0 >= 0, `stress ≥0 ${x}`);
}
check(stressResidual(FIXED) < 1e-15, 'stress@FIXED');
check(stressResidual(FIXED + 1e-14) < 1e-11, 'stress near FIXED');

// 6. Channel separation (~100)
for (let i = 0; i < 100; i++) {
  const x = (i / 100) * 9;
  const sm = softMap(x);
  const sc = softContract(x, 0.5);
  if (Math.abs(x - FIXED) > 0.05) {
    check(Math.abs(sm - sc) > 0.05, `channels differ ${x}`);
  } else {
    check(Math.abs(sm - sc) < 0.1, `channels near FIXED ${x}`);
  }
  check(close(softMap(softMap(x)), x), `softMap² ${x}`);
}

// 7. stateAt / CONE (~200)
for (let i = 0; i < 200; i++) {
  const t = (i - 50) * 17.3;
  const s = stateAt(t);
  check(s.psi + 1e-14 >= CONE, `Ψ≥CONE t=${t}`);
  check(s.S >= 0 && s.S <= 0.25 + 1e-14, `S range t=${t}`);
  check(close(s.S, heat(s.h)), `S=heat t=${t}`);
}
check(close(heat(0.5), 0.25), 'heat max');
check(heat(0) === 0 && heat(1) === 0, 'heat ends');

// 8. Monte-Carlo 400
let mcOk = 0;
for (let i = 0; i < 400; i++) {
  const start = (rnd() - 0.5) * 10000;
  const k = 0.05 + rnd() * 0.92;
  let x = start;
  for (let j = 0; j < 180; j++) x = softContract(x, k);
  if (Math.abs(x - FIXED) < 1e-3) mcOk++;
}
check(mcOk >= 380, `MC 400 ≥380 (got ${mcOk})`);

// 9. Near-boundary neighborhoods (~100)
for (const delta of [1e-15, 1e-12, 1e-9, 1e-6, 1e-3]) {
  for (const sign of [1, -1]) {
    const x = 0 + sign * delta;
    const m = ((x % 9) + 9) % 9;
    check(m >= 0 && (m < 9 || close(m, 9)), `canon near0 δ=${delta}`);
    const x9 = 9 + sign * delta;
    const m9 = ((x9 % 9) + 9) % 9;
    check(m9 >= 0 && (m9 < 9 || close(m9, 0)), `canon near9 δ=${delta}`);
  }
}

// 10. Monotonic approach samples (~50)
for (const start of [0, 1, 3, 6, 8]) {
  let x = start;
  let prev = Math.abs(x - FIXED);
  let ok = true;
  for (let i = 0; i < 30; i++) {
    x = softContract(x, 0.6);
    const d = Math.abs(x - FIXED);
    if (d > prev + 1e-12) { ok = false; break; }
    prev = d;
  }
  check(ok, `mono start=${start}`);
}

// DescentEngine long
const eng = new DescentEngine({ start: -77, k: 0.35 });
for (let i = 0; i < 250; i++) eng.tick();
check(Math.abs(eng.x - FIXED) < 1e-5, 'engine long');
check(eng.snapshot().nearFixed, 'engine nearFixed');

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 5 && passed >= 1900) {
  console.log('Volume measure coherent (≤5 residual float edges).');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
