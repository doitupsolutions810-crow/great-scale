const test = require('node:test');
const assert = require('node:assert/strict');
const {
  isValidResidualCoordinate,
  coneCompliant,
  fromTopologicalSaturation,
} = require('./public/residual.cjs');

test('accepts the closed topology-derived residual domain [0, 0.25]', () => {
  assert.equal(isValidResidualCoordinate(0), true);
  assert.equal(isValidResidualCoordinate(0.25), true);
  assert.equal(isValidResidualCoordinate(0.125), true);
  assert.equal(isValidResidualCoordinate(fromTopologicalSaturation(0).S), true);
  assert.equal(isValidResidualCoordinate(fromTopologicalSaturation(1).S), true);
});

test('rejects non-finite and out-of-domain residual values', () => {
  for (const value of [
    -1, -1e-13, 0.2500001, 100, NaN, Infinity, -Infinity, '0.1', null, undefined,
  ]) {
    assert.equal(isValidResidualCoordinate(value), false, `reject ${String(value)}`);
  }
});

test('cone lower-bound predicate is not a model-domain validator', () => {
  assert.equal(coneCompliant(100), true);
  assert.equal(isValidResidualCoordinate(100), false);
});
