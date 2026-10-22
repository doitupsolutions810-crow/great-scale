const assert = require('assert');
const {
  PHI, CONE, FIXED, heat, involution, involutionIdentity, modDist,
  twoCycles, fixedPoint, involutionFixedPoints, softMap, softContract, stressResidual,
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
test('contraction target is 4.5; circle involution fixed set is {0, 4.5}', () => {
  assert.strictEqual(fixedPoint(), 4.5);
  assert.deepStrictEqual(involutionFixedPoints(), [0, 4.5]);
  for (const x of involutionFixedPoints()) assert.ok(modDist(involution(x), x) < 1e-9);
});

test('softMap is involution: softMap(softMap(x))=x', () => {
  for (const x of [0, 1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9]) {
    assert.ok(Math.abs(softMap(softMap(x)) - x) < 1e-9, 'x=' + x);
  }
});
test('softMap(4.5)=4.5', () => assert.ok(Math.abs(softMap(4.5) - 4.5) < 1e-9));
test('stress residual vanishes at both circle fixed points', () => {
  assert.ok(stressResidual(0) < 1e-9);
  assert.ok(stressResidual(4.5) < 1e-9);
});
test('stress residual is circular distance to involution image', () => {
  assert.strictEqual(stressResidual(0), 0);
  assert.strictEqual(stressResidual(9), 0);
  assert.strictEqual(stressResidual(1), 2);
  assert.strictEqual(stressResidual(8), 2);
  assert.strictEqual(stressResidual(4), 1);
  assert.strictEqual(stressResidual(5), 1);
});
test('stress residual is periodic across the circle seam', () => {
  for (const x of [0, 0.25, 1, 2.5, 4.5, 7.75, 8.99]) {
    assert.ok(Math.abs(stressResidual(x) - stressResidual(x + 9)) < 1e-9, 'x=' + x);
    assert.ok(Math.abs(stressResidual(x) - stressResidual(x - 9)) < 1e-9, 'x=' + x);
  }
});
test('stress residual positive at non-fixed point x=2', () => assert.ok(stressResidual(2) > 0.5));

test('softContract rejects factors outside the strict contraction domain', () => {
  for (const k of [-2, -1, 1, 2, NaN, Infinity, -Infinity]) assert.throws(() => softContract(1, k), /contraction factor/);
  assert.throws(() => softContract(NaN, 0.5), /coordinate must be finite/);
});
test('public descentStep respects circle representatives and heat bounds', () => {
  for (const x of [-17, -8, 0, 1, 4.5, 8, 9, 10, 19, 28]) {
    const canonical = ((x % 9) + 9) % 9;
    for (const k of [-0.9, -0.5, 0, 0.5, 0.9]) {
      const y = descentStep(x, k);
      assert.ok(Math.abs(y - descentStep(canonical, k)) < 1e-12, 'periodic input x=' + x + ' k=' + k);
      assert.ok(y >= 0 && y < 9, 'circle-domain output y=' + y + ' k=' + k);
      const S = heat(y / 9);
      assert.ok(S >= 0 && S <= 0.25, 'heat invariant y=' + y + ' S=' + S);
    }
  }
  assert.strictEqual(descentStep(19, 0.5), descentStep(1, 0.5));
  assert.throws(() => descentStep(Infinity, 0.5), /circle coordinate/);
});

test('DescentEngine canonicalizes circle starts and rejects invalid k', () => {
  assert.strictEqual(new DescentEngine({start: 0}).x, new DescentEngine({start: 9}).x);
  assert.throws(() => new DescentEngine({start: 1, k: 1}), /contraction factor/);
  assert.throws(() => new DescentEngine({start: NaN}), /circle coordinate/);
  const eng = new DescentEngine({start: 19});
  assert.strictEqual(eng.x, 1);
  for (let i = 0; i < 40; i++) eng.tick();
  assert.ok(eng.history.every(r => r.S >= 0 && r.S <= 0.25));
});
test('DescentEngine validates timer interval bounds at construction and start', () => {
  for (const tickMs of [0, -1, NaN, Infinity, -Infinity, 2147483648]) {
    assert.throws(() => new DescentEngine({tickMs}), /tickMs/);
  }
  assert.strictEqual(new DescentEngine({tickMs: 1}).tickMs, 1);
  assert.strictEqual(new DescentEngine({tickMs: 2147483647}).tickMs, 2147483647);
  const eng = new DescentEngine({tickMs: 150});
  eng.tickMs = 0; // Public mutation must not bypass the start-time guard.
  assert.throws(() => eng.start(), /tickMs/);
  assert.strictEqual(eng.running, false);
  assert.strictEqual(eng.timer, null);
});
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
