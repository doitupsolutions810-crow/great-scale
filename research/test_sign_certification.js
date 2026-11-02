'use strict';
const assert = require('node:assert/strict');

// Bounded-uncertainty sign logic only; this does not validate an error model.
function certifySign(estimate, delta) {
  if (!Number.isFinite(estimate)) throw new TypeError('estimate must be finite');
  if (!Number.isFinite(delta) || delta < 0) throw new TypeError('delta must be finite and nonnegative');
  const lower = estimate - delta;
  const upper = estimate + delta;
  if (lower > 0) return { sign: 'positive', lower, upper };
  if (upper < 0) return { sign: 'negative', lower, upper };
  return { sign: 'unresolved', lower, upper };
}

assert.equal(certifySign(0.08, 0.03).sign, 'positive');
assert.equal(certifySign(-0.08, 0.03).sign, 'negative');
assert.equal(certifySign(0.02, 0.03).sign, 'unresolved');
assert.equal(certifySign(0.03, 0.03).sign, 'unresolved', 'lower endpoint touching zero is not strict');
assert.equal(certifySign(-0.03, 0.03).sign, 'unresolved', 'upper endpoint touching zero is not strict');
assert.equal(certifySign(1, 0).sign, 'positive');
assert.equal(certifySign(-1, 0).sign, 'negative');
assert.throws(() => certifySign(0.2, -0.1), /nonnegative/);
assert.throws(() => certifySign(NaN, 0.1), /finite/);
assert.throws(() => certifySign(0.2, Infinity), /finite/);
assert.equal(certifySign(0, 0).sign, 'unresolved');

console.log('PASS: 11 bounded-uncertainty sign assertions');
