'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const cjs = require('./public/scale.cjs');

(async () => {
  const source = fs.readFileSync(path.join(__dirname, 'public/scale.js'), 'utf8');
  // Import the exact ESM source as a data URL so this test works without
  // changing the repository-wide CommonJS package mode.
  const esm = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));

  const esmNames = Object.keys(esm).filter((key) => key !== 'default').sort();
  assert.deepEqual(esmNames, Object.keys(cjs).sort(),
    'named ES exports and CommonJS exports must have the same API');
  assert.deepEqual(Object.keys(esm.default).sort(), Object.keys(cjs).sort(),
    'ES default export and CommonJS export must have the same API');

  for (const key of ['PHI', 'PHI_INV', 'CONE', 'RATE', 'RESIDUAL_DIMS',
    'FIXED', 'CONE_MATRIX', 'FIB_MATRIX', 'HYPOTHESIS']) {
    assert.deepEqual(esm[key], cjs[key], key + ' must match between module formats');
    assert.deepEqual(esm.default[key], cjs[key], 'default.' + key + ' must match CommonJS');
  }

  const M = esm.CONE_MATRIX;
  const trace = M[0][0] + M[1][1];
  const determinant = M[0][0] * M[1][1] - M[0][1] * M[1][0];
  const discriminant = trace * trace - 4 * determinant;
  const lambdaPlus = (trace + Math.sqrt(discriminant)) / 2;
  const lambdaMinus = (trace - Math.sqrt(discriminant)) / 2;
  assert.equal(trace, 3, 'CONE matrix trace must match its characteristic polynomial');
  assert.equal(determinant, 1, 'CONE matrix determinant must be +1');
  assert.ok(Math.abs(lambdaPlus - esm.PHI ** 2) < 1e-12,
    'expanding eigenvalue must equal phi squared');
  assert.ok(Math.abs(lambdaMinus - esm.CONE) < 1e-12,
    'contracting eigenvalue must equal CONE');
  assert.ok(lambdaPlus > 1 && lambdaMinus > 0 && lambdaMinus < 1,
    'matrix must have distinct expanding and contracting eigendirections');

  assert.deepEqual(esm.twoCycles(), cjs.twoCycles(), 'two-cycle structure must match');
  assert.deepEqual(esm.fixedPoint(), cjs.fixedPoint(), 'fixed point must match');
  for (const h of [0, 0.25, 0.5, 0.75, 1]) {
    assert.deepEqual(esm.heat(h), cjs.heat(h), 'heat differs at h=' + h);
  }

  for (const x of [-1, 0, 1, 4.5, 8, 9, 10]) {
    for (const name of ['involution', 'modDist', 'involutionIdentity',
      'softContract', 'softMap', 'stressResidual', 'descentStep']) {
      const args = name === 'modDist' ? [x, 4.5] : [x];
      assert.deepEqual(esm[name](...args), cjs[name](...args),
        name + ' differs at input ' + x);
    }
  }

  for (const t of [0, 0.25, 1, 3.75, 12.5]) {
    assert.deepEqual(esm.stateAt(t), cjs.stateAt(t), 'stateAt differs at t=' + t);
  }

  const esmEngine = new esm.DescentEngine({ start: 1 });
  const cjsEngine = new cjs.DescentEngine({ start: 1 });
  assert.deepEqual(esmEngine.snapshot(), cjsEngine.snapshot(),
    'descent engine snapshots and version identifiers must match');
  assert.deepEqual(esmEngine.tick(), cjsEngine.tick(),
    'descent engine transition records must match');
  assert.deepEqual(esmEngine.snapshot(), cjsEngine.snapshot(),
    'descent engine post-step state must match');

  console.log('scale module parity: passed');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
