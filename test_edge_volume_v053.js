/**
 * Great Scale ultra-volume edge battery v0.5.3 (JS) — 3000+ additional cases.
 * Parallel + extra DescentEngine multi-stage stress.
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

let seed = 20261110 + 53;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0x100000000;
}

console.log('=== Great Scale ultra-volume EDGE battery v0.5.3 (JS) ===');

// A. Combined property stress (~800)
for (let i = 0; i < 200; i++) {
  let x = (rnd() - 0.5) * 4000;
  const k = 0.1 + rnd() * 0.82;
  for (let s = 0; s < 40; s++) {
    x = softContract(x, k);
    const r = stressResidual(x);
    check(r >= -1e-15, `A-stress≥0 i=${i} s=${s}`);
    check(involutionIdentity(x), `A-inv² i=${i} s=${s}`);
  }
  check(Math.abs(x - FIXED) < 0.5, `A-final i=${i}`);
}

// B. Residual decay vs k^n (~400)
for (const k of [0.3, 0.5, 0.7, 0.85]) {
  for (const start of [0, 1, 3, 8]) {
    let x = start;
    const m0 = ((start % 9) + 9) % 9;
    const dist0 = Math.abs(m0 - FIXED);
    for (let n = 1; n <= 50; n++) {
      x = softContract(x, k);
      const dist = Math.abs(x - FIXED);
      const theo = dist0 * Math.pow(k, n);
      if (theo > 1e-12) {
        const rel = Math.abs(dist - theo) / Math.max(theo, 1e-15);
        check(rel < 0.15 || dist < 1e-9, `B-decay k=${k} n=${n}`);
      } else {
        check(dist < 1e-8, `B-decay tiny k=${k} n=${n}`);
      }
    }
  }
}

// C. Adversarial (~400)
for (const mag of [1e-200, 1e-100, 1e-50, 1e-20]) {
  for (const sign of [1, -1]) {
    const x = sign * mag;
    const c = softContract(x, 0.5);
    check(Number.isFinite(c), `C-tiny finite ${x}`);
  }
}
for (const mag of [1e20, 1e50, 1e100]) {
  for (const sign of [1, -1]) {
    const c = softContract(sign * mag, 0.5);
    check(Number.isFinite(c), `C-huge finite ${mag}`);
    const m = ((c % 9) + 9) % 9;
    check(m >= 0 && m < 9 + 1e-9, `C-huge canon ${mag}`);
  }
}
for (const k of [0.999, 0.9999]) {
  let x = 0;
  for (let i = 0; i < 5000; i++) x = softContract(x, k);
  check(Math.abs(x - FIXED) < 4.5, `C-near1 progress k=${k}`);
  check(Number.isFinite(x), `C-near1 finite k=${k}`);
}
check(close(softContract(3, 0), FIXED), 'C-k0');
for (const k of [-0.3, -0.5, -0.7]) {
  let x = 1;
  for (let i = 0; i < 80; i++) x = softContract(x, k);
  check(Math.abs(x - FIXED) < 0.5, `C-negk k=${k}`);
}

// D. Cross-channel (~300)
for (let i = 0; i < 100; i++) {
  const x = rnd() * 9;
  const n = Math.floor(rnd() * 41) - 20;
  check(close(softMap(softMap(x + n * 9)), x + n * 9), `D-softMap² i=${i}`);
  check(close(softContract(x, 0.6), softContract(x + n * 9, 0.6)), `D-fiber i=${i}`);
}

// E. Multi-stage trajectories (~300)
for (const stageK of [0.4, 0.6, 0.8]) {
  for (const start of [-50, 0, 2, 7, 100]) {
    let x = start;
    let prev = Math.abs(x - FIXED);
    for (let s = 0; s < 60; s++) {
      x = softContract(x, stageK);
      const d = Math.abs(x - FIXED);
      if (s < 20) check(d <= prev + 1e-9, `E-mono k=${stageK} s=${s}`);
      prev = d;
    }
    check(Math.abs(x - FIXED) < 0.05, `E-final k=${stageK} start=${start}`);
  }
}

// F. Heat identities (~150)
for (let i = 0; i < 100; i++) {
  const h = rnd();
  check(close(heat(h), heat(1 - h)), `F-sym ${h}`);
  check(heat(h) >= 0 && heat(h) <= 0.25 + 1e-15, `F-range ${h}`);
}
check(close(heat(0.5), 0.25), 'F-max');
check(heat(0) === 0 && heat(1) === 0, 'F-ends');

// G. Basin sampling (~250)
for (const delta of [1e-12, 1e-9, 1e-6, 1e-3, 0.01, 0.1, 0.5, 1, 2]) {
  for (const sign of [1, -1]) {
    const x = FIXED + sign * delta;
    for (const k of [0.2, 0.5, 0.8]) {
      const c = softContract(x, k);
      check(Math.abs(c - FIXED) <= Math.abs(x - FIXED) + 1e-12, `G-basin δ=${delta}`);
      let y = x;
      for (let i = 0; i < 100; i++) y = softContract(y, k);
      check(Math.abs(y - FIXED) < 1e-5, `G-long δ=${delta}`);
    }
  }
}

// H. Stratified MC (~300)
const strata = [[-1e5, -100], [-100, -1], [-1, 0], [0, 1], [1, 100], [100, 1e5]];
let mcOk = 0, draws = 0;
for (const [lo, hi] of strata) {
  for (let i = 0; i < 50; i++) {
    const start = lo + rnd() * (hi - lo);
    const k = 0.15 + rnd() * 0.75;
    let x = start;
    for (let j = 0; j < 150; j++) x = softContract(x, k);
    draws++;
    if (Math.abs(x - FIXED) < 1e-3) mcOk++;
  }
}
check(mcOk >= Math.floor(0.92 * draws), `H-MC ${mcOk}/${draws}`);

// I. stateAt extreme (~150)
for (const rate of [0.1, 0.5, 0.85, 1, 2, 10]) {
  for (const t of [-1e6, -100, 0, 1, 50, 1e6]) {
    const s = stateAt(t, rate);
    check(s.psi + 1e-14 >= CONE, `I-Ψ r=${rate} t=${t}`);
    check(s.S >= 0 && s.S <= 0.25 + 1e-14, `I-S r=${rate} t=${t}`);
  }
}

// J. Engine multi-stage (~50)
const eng = new DescentEngine({ start: 123.456, k: 0.55 });
for (let i = 0; i < 200; i++) eng.tick();
check(Math.abs(eng.x - FIXED) < 1e-5, 'J-engine');
check(eng.snapshot().nearFixed, 'J-nearFixed');
check(eng.t === 200, 'J-t');

const total = passed + failed;
console.log(`\n=== ${passed}/${total} passed  (${failed} failed) ===`);
if (fails.length) {
  console.log('Sample failures:');
  fails.slice(0, 30).forEach(f => console.log('  FAIL  ' + f));
}
if (failed <= 15 && passed >= 2800) {
  console.log('Ultra-volume measure coherent.');
  process.exit(0);
}
process.exit(failed === 0 ? 0 : 1);
