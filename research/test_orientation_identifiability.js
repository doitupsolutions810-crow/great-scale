'use strict';
const assert = require('node:assert/strict');

// Abstract states motivated by the Great Scale channel-identifiability question.
// This is an algebraic regression, not a Chern-number numerical solver.
const plus = Object.freeze({ greatScale: 0.75, entropy: 0.25, signedInvariant: 1 });
const minus = Object.freeze({ greatScale: 0.75, entropy: 0.25, signedInvariant: -1 });

const unsignedProjection = state => [state.greatScale, state.entropy];
const augmentedObservation = state => [...unsignedProjection(state), state.signedInvariant];

assert.deepEqual(unsignedProjection(plus), unsignedProjection(minus),
  'unsigned channels must exhibit the intended collision');
assert.equal(plus.signedInvariant, -minus.signedInvariant,
  'signed invariant must reverse');
assert.notEqual(plus.signedInvariant, 0);
assert.notEqual(minus.signedInvariant, 0);
assert.notDeepEqual(augmentedObservation(plus), augmentedObservation(minus),
  'adding the signed channel must distinguish this pair');
assert.equal(unsignedProjection(plus).length, 2,
  'the lossy projection must not silently include the signed channel');

console.log('PASS: 6 orientation-identifiability assertions');
