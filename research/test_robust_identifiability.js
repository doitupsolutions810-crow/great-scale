'use strict';
const assert = require('node:assert/strict');

function euclideanDistance(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b) || a.length === 0 || a.length !== b.length) {
    throw new TypeError('observations must be nonempty arrays of equal length');
  }
  if (![...a, ...b].every(Number.isFinite)) throw new TypeError('coordinates must be finite');
  return Math.sqrt(a.reduce((sum, v, i) => sum + (v - b[i]) ** 2, 0));
}
function robustlyDistinguishable(a, b, epsilon) {
  if (!Number.isFinite(epsilon) || epsilon < 0) throw new TypeError('epsilon must be finite and nonnegative');
  const distance = euclideanDistance(a, b);
  return { distance, margin: distance - 2 * epsilon, certified: distance > 2 * epsilon };
}
const unsignedPlus = [0, 0];
const unsignedMinus = [0, 0];
assert.equal(robustlyDistinguishable(unsignedPlus, unsignedMinus, 0).certified, false);
const signedPlus = [0, 0, 1];
const signedMinus = [0, 0, -1];
assert.equal(robustlyDistinguishable(signedPlus, signedMinus, 0.4).certified, true);
assert.equal(robustlyDistinguishable(signedPlus, signedMinus, 1).certified, false, 'touching balls are not disjoint');
assert.equal(robustlyDistinguishable(signedPlus, signedMinus, 1.01).certified, false);
assert.equal(robustlyDistinguishable(signedPlus, signedMinus, 0.99).certified, true);
assert.equal(robustlyDistinguishable([1], [1], 0).distance, 0);
assert.equal(robustlyDistinguishable([0, 0], [3, 4], 2).distance, 5);
assert.equal(robustlyDistinguishable([0, 0], [3, 4], 2).certified, true);
assert.throws(() => robustlyDistinguishable([1], [1, 2], 0), /equal length/);
assert.throws(() => robustlyDistinguishable([NaN], [1], 0), /finite/);
assert.throws(() => robustlyDistinguishable([1], [2], -0.1), /nonnegative/);
console.log('PASS: 11 robust-distinguishability assertions');
