const assert = require('assert');
const {
  PHI, CONE, FIXED, heat, involution, involutionIdentity, modDist,
  twoCycles, fixedPoint, softMap, softContract, stressResidual,
  descentStep, stateAt, DescentEngine, HYPOTHESIS,
} = require('./public/scale.cjs');
const { computeRiskCertificate, computeMomentLogLossBound, classifyRisk } = require('./public/risk-certificate.js');
const { computeRobustDescentCertificate } = require('./public/descent-certificate.js');

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

test('stress residual contracts exactly by |k| on signed descent orbits', () => {
  for (const k of [0.5, -0.75, 0]) {
    const eng = new DescentEngine({ start: 2.0, k });
    let previous = stressResidual(eng.x);
    for (let i = 0; i < 8; i++) {
      eng.tick();
      const current = stressResidual(eng.x);
      assert.ok(Math.abs(current - Math.abs(k) * previous) < 1e-10, 'k=' + k + ' step=' + i);
      previous = current;
    }
  }
});

test('bounded disturbances obey the projected finite-step residual certificate', () => {
  const initialResidual = 5;
  const disturbanceBound = 0.13;
  const steps = 7;

  for (const k of [0, 0.75, -0.65, 0.99]) {
    const certificate = computeRobustDescentCertificate({ initialResidual, k, disturbanceBound, steps });
    for (let signs = 0; signs < 2 ** steps; signs++) {
      let x = FIXED + initialResidual / 2;
      for (let index = 0; index < steps; index++) {
        const disturbance = (signs & (1 << index) ? 1 : -1) * disturbanceBound;
        x = Math.max(1, Math.min(8, FIXED + k * (x - FIXED) + disturbance));
      }
      assert.ok(stressResidual(x) <= certificate.residualUpperBound + 1e-12, `k=${k} signs=${signs}`);
    }
  }
});

test('robust descent certificate recovers the exact zero-noise orbit and limiting bound', () => {
  const initialResidual = 5;
  const k = -0.5;
  const exact = computeRobustDescentCertificate({ initialResidual, k, disturbanceBound: 0, steps: 8 });
  assert.ok(Math.abs(exact.residualUpperBound - initialResidual * Math.abs(k) ** 8) < 1e-12);

  const noisy = computeRobustDescentCertificate({ initialResidual, k, disturbanceBound: 0.1, steps: 100 });
  assert.ok(noisy.residualUpperBound <= noisy.ultimateResidualUpperBound + initialResidual * Math.abs(k) ** 100 + 1e-12);
  assert.ok(Math.abs(noisy.ultimateResidualUpperBound - 0.4) < 1e-12);
  assert.strictEqual(noisy.normalizedUltimateResidualUpperBound, noisy.ultimateResidualUpperBound / 7);
});

test('robust descent certificate rejects invalid domains and parameters', () => {
  for (const input of [
    { initialResidual: 7.01, k: 0.5, disturbanceBound: 0, steps: 1 },
    { initialResidual: 1, k: 1, disturbanceBound: 0, steps: 1 },
    { initialResidual: 1, k: 0.5, disturbanceBound: -0.1, steps: 1 },
    { initialResidual: 1, k: 0.5, disturbanceBound: 0.1, steps: -1 },
    { initialResidual: 1, k: 0.5, disturbanceBound: 0.1, steps: 1.5 },
  ]) assert.throws(() => computeRobustDescentCertificate(input));
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

test('risk certificate covers the known constant-rate risk', () => {
  const certificate = computeRiskCertificate({
    successes: Array(1000).fill(500000),
    trialsPerGroup: 1000000,
    supportGap: 0.1,
    confidence: 0.95,
  });
  const exactRisk = -Math.log(0.5);
  assert.ok(certificate.lowerBound <= exactRisk);
  assert.ok(exactRisk <= certificate.upperBound);
});
test('risk certificate reports separate uncertainty components', () => {
  const certificate = computeRiskCertificate({
    successes: [50, 50, 50], trialsPerGroup: 100, supportGap: 0.1,
  });
  assert.ok(certificate.measurementRadius > 0);
  assert.ok(certificate.samplingRadius > 0);
  assert.strictEqual(certificate.radius, certificate.measurementRadius + certificate.samplingRadius);
});
test('more within-group trials cannot remove between-group uncertainty', () => {
  const fewerRepeats = computeRiskCertificate({
    successes: Array(1000).fill(500), trialsPerGroup: 1000, supportGap: 0.1,
  });
  const moreRepeats = computeRiskCertificate({
    successes: Array(1000).fill(5000), trialsPerGroup: 10000, supportGap: 0.1,
  });
  assert.strictEqual(fewerRepeats.samplingRadius, moreRepeats.samplingRadius);
  assert.ok(moreRepeats.measurementRadius < fewerRepeats.measurementRadius);
  assert.ok(fewerRepeats.samplingRadius > 0.05);
});
test('risk certificate clips observed rates at declared support', () => {
  const certificate = computeRiskCertificate({
    successes: [100], trialsPerGroup: 100, supportGap: 0.1,
  });
  assert.ok(Math.abs(certificate.center - certificate.maximumLoss) < 1e-12);
});
test('smaller support gap increases measurement sensitivity', () => {
  const input = { successes: [50, 50], trialsPerGroup: 100, confidence: 0.95 };
  const widerGap = computeRiskCertificate({ ...input, supportGap: 0.1 });
  const narrowerGap = computeRiskCertificate({ ...input, supportGap: 0.05 });
  assert.ok(narrowerGap.measurementRadius > widerGap.measurementRadius);
});
test('higher confidence widens the risk interval', () => {
  const input = { successes: [50, 50], trialsPerGroup: 100, supportGap: 0.1 };
  const standard = computeRiskCertificate({ ...input, confidence: 0.9 });
  const stricter = computeRiskCertificate({ ...input, confidence: 0.99 });
  assert.ok(stricter.radius > standard.radius);
});
test('risk limit classification handles pass, fail, and indeterminate', () => {
  assert.strictEqual(classifyRisk({ lowerBound: 0.2, upperBound: 0.4 }, 0.4), 'within-limit');
  assert.strictEqual(classifyRisk({ lowerBound: 0.5, upperBound: 0.7 }, 0.4), 'above-limit');
  assert.strictEqual(classifyRisk({ lowerBound: 0.2, upperBound: 0.7 }, 0.4), 'indeterminate');
});
test('risk certificate rejects invalid sampling and support inputs', () => {
  assert.throws(() => computeRiskCertificate({ successes: [], trialsPerGroup: 1, supportGap: 0.1 }));
  assert.throws(() => computeRiskCertificate({ successes: [2], trialsPerGroup: 1, supportGap: 0.1 }));
  assert.throws(() => computeRiskCertificate({ successes: [0], trialsPerGroup: Number.MAX_SAFE_INTEGER + 1, supportGap: 0.1 }));
  assert.throws(() => computeRiskCertificate({ successes: [Number.MAX_SAFE_INTEGER + 1], trialsPerGroup: Number.MAX_SAFE_INTEGER, supportGap: 0.1 }));
  assert.throws(() => computeRiskCertificate({ successes: Array(10001).fill(0), trialsPerGroup: 1, supportGap: 0.1 }));
  assert.throws(() => computeRiskCertificate({ successes: [0], trialsPerGroup: 1, supportGap: 0 }));
  assert.throws(() => computeRiskCertificate({ successes: [0], trialsPerGroup: 1, supportGap: Number.MIN_VALUE }));
  assert.throws(() => computeRiskCertificate({ successes: [0], trialsPerGroup: 1, supportGap: 0.1, scale: Number.MAX_VALUE }));
  assert.throws(() => computeMomentLogLossBound({ mean: 0, variance: 0, supportGap: Number.MIN_VALUE }));
  assert.throws(() => computeMomentLogLossBound({ mean: 0.5, variance: 0.01, supportGap: 1e-8, scale: Number.MAX_VALUE }));
  assert.throws(() => classifyRisk({ lowerBound: 0, upperBound: 1 }, -1));
});

test('moment bound encloses fixed-moment risks as the boundary is approached', () => {
  const mean = 0.5;
  const variance = 0.04;
  const tailMass = 0.1;
  let previousLoss = -Infinity;

  for (const supportGap of [1e-2, 1e-4, 1e-8, 1e-12]) {
    const boundaryPoint = 1 - supportGap;
    const remainingMean = (mean - tailMass * boundaryPoint) / (1 - tailMass);
    const remainingSecondMoment = (mean * mean + variance - tailMass * boundaryPoint * boundaryPoint)
      / (1 - tailMass);
    const spread = Math.sqrt(remainingSecondMoment - remainingMean * remainingMean);
    const supportPoints = [boundaryPoint, remainingMean - spread, remainingMean + spread];
    const probabilities = [tailMass, (1 - tailMass) / 2, (1 - tailMass) / 2];
    const exactLoss = supportPoints.reduce((total, point, index) => (
      total - probabilities[index] * Math.log1p(-point)
    ), 0);
    const bound = computeMomentLogLossBound({ mean, variance, supportGap });

    assert.ok(supportPoints.every(point => point >= 0 && point <= boundaryPoint));
    assert.ok(Math.abs(supportPoints.reduce((total, point, index) => total + probabilities[index] * point, 0) - mean) < 1e-10);
    assert.ok(Math.abs(supportPoints.reduce((total, point, index) => total + probabilities[index] * (point - mean) ** 2, 0) - variance) < 1e-10);
    assert.ok(bound.lowerBound <= exactLoss + 1e-12);
    assert.ok(bound.lowerBound >= bound.jensenLowerBound - 1e-12);
    assert.ok(exactLoss <= bound.chordUpperBound + 1e-12);
    assert.ok(exactLoss <= bound.curvatureUpperBound + 1e-12);
    assert.ok(exactLoss <= bound.secondMomentUpperBound + 1e-12);
    assert.ok(exactLoss <= bound.upperBound + 1e-12);
    assert.ok(Number.isFinite(bound.upperBound));
    assert.ok(exactLoss > previousLoss);
    previousLoss = exactLoss;
  }
});

test('sharp moment bounds are attained by their reported two-point witnesses', () => {
  const bound = computeMomentLogLossBound({ mean: 0.5, variance: 0.04, supportGap: 0.1 });
  const stats = distribution => {
    const mean = distribution.reduce((sum, point) => sum + point.value * point.probability, 0);
    const variance = distribution.reduce((sum, point) => (
      sum + point.probability * (point.value - mean) ** 2
    ), 0);
    const loss = distribution.reduce((sum, point) => (
      sum - point.probability * Math.log1p(-point.value)
    ), 0);
    return { mean, variance, loss };
  };

  for (const [distribution, expectedLoss] of [
    [bound.lowerExtremizer, bound.lowerBound],
    [bound.upperExtremizer, bound.upperBound],
  ]) {
    const witness = stats(distribution);
    assert.ok(Math.abs(witness.mean - bound.mean) < 1e-12);
    assert.ok(Math.abs(witness.variance - bound.variance) < 1e-12);
    assert.ok(Math.abs(witness.loss - expectedLoss) < 1e-12);
    assert.ok(distribution.every(point => point.value >= 0 && point.value <= bound.supportMaximum));
  }
  assert.ok(bound.lowerBound <= bound.upperBound);
  assert.strictEqual(bound.boundType, 'sharp-moment-extremal');
  assert.strictEqual(bound.greatScaleStatus, 'conditional research sidecar; no canonical level assigned');
});

test('sharp moment interval encloses varied finite-support distributions', () => {
  const distributions = [
    [{ value: 0.1, probability: 0.2 }, { value: 0.35, probability: 0.5 }, { value: 0.8, probability: 0.3 }],
    [{ value: 0, probability: 0.25 }, { value: 0.2, probability: 0.25 }, { value: 0.6, probability: 0.25 }, { value: 0.9, probability: 0.25 }],
    [{ value: 0.15, probability: 0.7 }, { value: 0.65, probability: 0.3 }],
  ];

  for (const distribution of distributions) {
    const mean = distribution.reduce((sum, point) => sum + point.value * point.probability, 0);
    const variance = distribution.reduce((sum, point) => (
      sum + point.probability * (point.value - mean) ** 2
    ), 0);
    const expectedLoss = distribution.reduce((sum, point) => (
      sum - point.probability * Math.log1p(-point.value)
    ), 0);
    const bound = computeMomentLogLossBound({ mean, variance, supportGap: 0.1 });

    assert.ok(bound.lowerBound <= expectedLoss + 1e-12);
    assert.ok(expectedLoss <= bound.upperBound + 1e-12);
  }
});

test('sharp moment bounds collapse for constants and coincide at maximum variance', () => {
  const constant = computeMomentLogLossBound({ mean: 0.4, variance: 0, supportGap: 0.1 });
  assert.ok(Math.abs(constant.lowerBound - constant.upperBound) < 1e-12);
  assert.strictEqual(constant.boundaryMass, 0);
  assert.strictEqual(constant.asymptoticLogLossCoefficient, 0);

  const maximumVariance = 0.4 * (0.9 - 0.4);
  const endpointMixture = computeMomentLogLossBound({ mean: 0.4, variance: maximumVariance, supportGap: 0.1 });
  assert.ok(Math.abs(endpointMixture.lowerBound - endpointMixture.upperBound) < 1e-12);
});

test('sharp upper tail coefficient is exact and its finite remainder converges', () => {
  const mean = 0.5;
  const variance = 0.04;
  const scale = 2.3;
  const asymptoticMass = variance / (variance + (1 - mean) ** 2);
  const limitingLowerAtom = mean - variance / (1 - mean);
  const limitingRemainder = scale * (1 - asymptoticMass) * -Math.log1p(-limitingLowerAtom);
  let previousMassError = Infinity;
  let lastRemainderError = Infinity;

  for (const supportGap of [1e-2, 1e-4, 1e-6, 1e-8]) {
    const bound = computeMomentLogLossBound({ mean, variance, supportGap, scale });
    const massError = Math.abs(bound.boundaryMass - asymptoticMass);
    const remainder = bound.upperBound - bound.asymptoticLogLossCoefficient * Math.log(1 / supportGap);

    assert.ok(Math.abs(bound.asymptoticBoundaryMass - asymptoticMass) < 1e-15);
    assert.ok(Math.abs(bound.asymptoticLogLossCoefficient - scale * asymptoticMass) < 1e-15);
    assert.ok(massError < previousMassError);
    assert.ok(Math.abs(remainder - limitingRemainder) < lastRemainderError);
    previousMassError = massError;
    lastRemainderError = Math.abs(remainder - limitingRemainder);
  }
  assert.ok(lastRemainderError < 1e-6);
});

test('moment bound rejects impossible moment/support combinations', () => {
  assert.throws(() => computeMomentLogLossBound({ mean: 0.95, variance: 0.01, supportGap: 0.1 }));
  assert.throws(() => computeMomentLogLossBound({ mean: 0.5, variance: 0.3, supportGap: 0.1 }));
  assert.throws(() => computeMomentLogLossBound({ mean: 0.5, variance: 0.04, supportGap: 0 }));
});

test('small-support series coefficient includes a conservative remainder', () => {
  const supportMaximum = 1e-4;
  const supportGap = 1 - supportMaximum;
  const mean = supportMaximum / 2;
  const bound = computeMomentLogLossBound({
    mean,
    variance: 0,
    supportGap,
  });
  const partial = Array.from({ length: 19 }, (_, index) => (
    supportMaximum ** index / (index + 2)
  )).reduce((sum, value) => sum + value, 0);
  const exactLoss = -Math.log1p(-mean);

  assert.ok(bound.secondMomentCoefficient >= partial);
  assert.ok(bound.secondMomentUpperBound >= exactLoss);
  assert.strictEqual(bound.decisionScope, 'conditional-model-only');
  assert.strictEqual(bound.evidenceVerified, false);
});

console.log('\ngreat-scale tests: ' + passed + ' passed, ' + failed + ' failed');
process.exit(failed ? 1 : 0);
