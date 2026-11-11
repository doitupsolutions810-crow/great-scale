/**
 * Great Scale edge-case battery v0.5.1 — longer, more robust.
 * Pushes quotient seams, extreme scales, non-finite guards,
 * long-horizon contraction, channel separation, and Monte-Carlo.
 */
'use strict';
const assert = require('assert');
const {
  PHI, CONE, FIXED, heat, involution, involutionIdentity, modDist,
  twoCycles, fixedPoint, softMap, softContract, stressResidual,
  stateAt, DescentEngine, HYPOTHESIS,
} = require('./public/scale.cjs');

let passed = 0, failed = 0;
function test(name, fn) {
  try {
    fn();
    passed++;
    console.log('  PASS  ' + name);
  } catch (e) {
    failed++;
    console.log('  FAIL  ' + name + ' — ' + e.message);
  }
}
function close(a, b, t = 1e-10) {
  assert.ok(Math.abs(a - b) <= t, `${a} != ${b}`);
}

// --- Core still holds ---
test('PHI / CONE constants', () => {
  close(PHI, 1.618033988749895, 1e-12);
  close(CONE, PHI ** -2, 1e-12);
  close(CONE, 0.3819660112501051, 1e-12);
});

test('heat law endpoints and max', () => {
  assert.strictEqual(heat(0), 0);
  assert.strictEqual(heat(1), 0);
  close(heat(0.5), 0.25);
  close(heat(0.2), heat(0.8));
});

// --- Wide-range involution identity ---
test('involution modular identity over [-100,100]', () => {
  for (let x = -100; x <= 100; x += 0.25) {
    assert.ok(involutionIdentity(x), 'x=' + x);
  }
});

test('two-cycles and fixed point', () => {
  for (const [a, b] of twoCycles()) {
    assert.strictEqual(involution(a), b);
    assert.strictEqual(involution(b), a);
  }
  close(involution(FIXED), FIXED);
  assert.strictEqual(fixedPoint(), FIXED);
});

// --- Extreme multi-wrap seams ---
test('softContract seam invariance under large integer offsets', () => {
  const offsets = [0, 9, -9, 18, -18, 90, -90, 900, -900, 9000];
  for (const off of offsets) {
    const c0 = softContract(0 + off);
    const c9 = softContract(9 + off);
    close(c0, c9, 1e-12);
    assert.ok(modDist(c0, c9) < 1e-12);
  }
});

test('fiber constancy across integer lattice', () => {
  const base = softContract(2.3, 0.3);
  for (let n = -30; n <= 30; n++) {
    close(softContract(2.3 + n * 9, 0.3), base, 1e-12);
  }
});

// --- Long-horizon under varied k ---
// For |k| close to 1 contraction is intentionally slow; use scale-aware tolerance.
test('long-horizon contraction k in (0,1) from many starts', () => {
  const ks = [0.1, 0.3, 0.5, 0.7, 0.9, 0.99];
  const starts = [0, 0.01, 1, 4.499, 4.501, 8.99, 9, -100, 1e6, -1e5];
  for (const k of ks) {
    const tol = k <= 0.9 ? 1e-4 : 0.05;
    const steps = k <= 0.9 ? 200 : 600;
    for (const start of starts) {
      let x = start;
      for (let i = 0; i < steps; i++) x = softContract(x, k);
      assert.ok(Math.abs(x - FIXED) < tol,
        `k=${k} start=${start} final=${x} tol=${tol}`);
    }
  }
});

test('k approaching 1 still contracts after many steps', () => {
  let x = 0;
  for (let i = 0; i < 3000; i++) x = softContract(x, 0.999);
  assert.ok(Math.abs(x - FIXED) < 0.25, 'final=' + x);
});

// --- Stress residual representation invariance ---
test('stress residual invariant on integer fibers', () => {
  for (const x of [0, 1, 2, 3.7, 4.5, 5.1, 8.9]) {
    const r0 = stressResidual(x);
    for (let n = -8; n <= 8; n++) {
      close(stressResidual(x + n * 9), r0, 1e-12);
    }
  }
});

test('stress vanishes at and near FIXED', () => {
  assert.ok(stressResidual(FIXED) < 1e-15);
  assert.ok(stressResidual(FIXED + 1e-14) < 1e-12);
});

// --- Channel separation ---
test('softMap pure involution; softContract contraction; agree only at FIXED', () => {
  for (const x of [0.5, 1, 2, 3, 6, 7.5]) {
    assert.ok(Math.abs(softMap(x) - softContract(x, 0.5)) > 0.1);
  }
  close(softMap(FIXED), softContract(FIXED, 0.5));
  // softMap is involution even after large translation
  for (const x of [0, 1, 2, 3, 4, 4.5, 5, 6, 7, 8]) {
    const y = softMap(softMap(x + 27));
    assert.ok(modDist(y, x) < 1e-9 || Math.abs(y - (x % 9)) < 1e-9);
  }
});

// --- stateAt phase wrap + CONE floor ---
test('stateAt Ψ ≥ CONE for extreme t', () => {
  for (const t of [0, 0.5, 1, 10, 100, 1e6, -1e3, 1e9]) {
    const s = stateAt(t);
    assert.ok(s.psi + 1e-14 >= CONE, `t=${t} psi=${s.psi}`);
    assert.ok(s.S >= 0 && s.S <= 0.25 + 1e-14);
  }
});

// --- DescentEngine long run ---
test('DescentEngine long-horizon snapshot', () => {
  const eng = new DescentEngine({ start: -50, k: 0.4 });
  for (let i = 0; i < 300; i++) eng.tick();
  assert.ok(Math.abs(eng.x - FIXED) < 1e-5);
  assert.ok(eng.snapshot().nearFixed);
  assert.strictEqual(eng.t, 300);
});

// --- Monte-Carlo seeded ---
test('Monte-Carlo 40 random starts converge', () => {
  // simple LCG for determinism
  let seed = 42;
  function rnd() {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 0x100000000;
  }
  let ok = 0;
  for (let i = 0; i < 40; i++) {
    const start = (rnd() - 0.5) * 2000;
    const k = 0.05 + rnd() * 0.9;
    let x = start;
    for (let j = 0; j < 150; j++) x = softContract(x, k);
    if (Math.abs(x - FIXED) < 1e-4) ok++;
  }
  assert.ok(ok >= 38, `only ${ok}/40 converged`);
});

// --- Hypothesis still present ---
test('HYPOTHESIS statements intact', () => {
  assert.ok(HYPOTHESIS.statements.length >= 6);
  assert.ok(HYPOTHESIS.statements.some(s => s.includes('circle-native')));
  assert.ok(HYPOTHESIS.statements.some(s => s.includes('Never claim certainty')));
});

// --- Non-finite defensive (softContract on extreme finite) ---
test('softContract on large finite stays finite', () => {
  const x = softContract(1e20);
  assert.ok(Number.isFinite(x));
  assert.ok(x >= 0 && x <= 9);
});

console.log(`\ngreat-scale EDGE tests: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
