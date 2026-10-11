const assert = require('assert');
const {
  PHI, CONE, FIXED, heat, involution, involutionIdentity, modDist,
  twoCycles, fixedPoint, softMap, softContract, stressResidual,
  descentStep, stateAt, DescentEngine, HYPOTHESIS,
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

test('PHI golden ratio', () => assert.ok(Math.abs(PHI - 1.618034) < 1e-5));
test('CONE = φ⁻² ≈ 0.382', () => assert.ok(Math.abs(CONE - 0.381966) < 1e-5));
test('heat(0.5) = 0.25', () => assert.strictEqual(heat(0.5), 0.25));
test('heat symmetric', () => assert.ok(Math.abs(heat(0.2) - heat(0.8)) < 1e-12));
test('heat endpoints zero', () => {
  assert.strictEqual(heat(0), 0);
  assert.strictEqual(heat(1), 0);
});

test('involution modular identity on [0,9]', () => {
  for (let x = 0; x <= 9; x += 0.25) {
    assert.ok(involutionIdentity(x), 'x=' + x + ' f(f)=' + involution(involution(x)));
  }
});
test('involution boundary: 0 and 9 both map to 0 (circle)', () => {
  assert.strictEqual(involution(0), 0);
  assert.strictEqual(involution(9), 0);
  assert.ok(modDist(0, 9) === 0 || modDist(involution(9), 0) < 1e-9);
});
test('two-cycles preserved', () => {
  for (const [a, b] of twoCycles()) {
    assert.strictEqual(involution(a), b);
    assert.strictEqual(involution(b), a);
  }
});
test('fixed point 4.5', () => {
  assert.strictEqual(fixedPoint(), 4.5);
  assert.ok(Math.abs(involution(4.5) - 4.5) < 1e-9);
});

test('softMap is involution: softMap(softMap(x))=x', () => {
  for (const x of [0, 1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9]) {
    assert.ok(Math.abs(softMap(softMap(x)) - x) < 1e-9, 'x=' + x);
  }
});
test('softMap(4.5)=4.5', () => assert.ok(Math.abs(softMap(4.5) - 4.5) < 1e-9));
test('stress residual zero at fixed point', () => assert.ok(stressResidual(4.5) < 1e-9));
test('stress residual positive off fixed point', () => assert.ok(stressResidual(2) > 0.5));

test('soft contraction converges to 4.5 from 1.0', () => {
  let x = 1.0;
  for (let i = 0; i < 40; i++) x = softContract(x, 0.5);
  assert.ok(Math.abs(x - 4.5) < 1e-6, 'x=' + x);
});
test('soft contraction converges from 8.0', () => {
  let x = 8.0;
  for (let i = 0; i < 40; i++) x = softContract(x, 0.5);
  assert.ok(Math.abs(x - 4.5) < 1e-6, 'x=' + x);
});
test('soft contraction multi-start', () => {
  for (const start of [0.5, 2, 3, 6, 8.5]) {
    let x = start;
    for (let i = 0; i < 50; i++) x = softContract(x, 0.5);
    assert.ok(Math.abs(x - 4.5) < 1e-6, 'start=' + start + ' x=' + x);
  }
});

test('DescentEngine converges', () => {
  const eng = new DescentEngine({ start: 1.0, k: 0.5 });
  for (let i = 0; i < 40; i++) eng.tick();
  assert.ok(Math.abs(eng.x - 4.5) < 1e-6, 'engine x=' + eng.x);
  assert.ok(eng.t === 40);
  assert.ok(eng.snapshot().nearFixed);
});

test('stateAt: Ψ = CONE + S never below CONE', () => {
  for (const t of [0, 0.5, 1, 2, 3.14, 10]) {
    const s = stateAt(t);
    assert.ok(s.psi + 1e-12 >= CONE, 't=' + t + ' psi=' + s.psi);
    assert.ok(s.S >= 0 && s.S <= 0.25);
  }
});
test('stateAt: λ may be below CONE at low heat (allowed)', () => {
  const s = stateAt(0);
  assert.ok(s.lam < CONE || s.S > 0.1);
});

test('hypothesis present', () => {
  assert.ok(HYPOTHESIS.statements.length >= 4);
  assert.ok(HYPOTHESIS.statements.some((s) => s.includes('h(1-h)')));
});

console.log('\ngreat-scale tests: ' + passed + ' passed, ' + failed + ' failed');
process.exit(failed ? 1 : 0);
