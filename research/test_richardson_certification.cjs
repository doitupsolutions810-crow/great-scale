'use strict';
// Counterexample to treating adjacent midpoint-grid differences as rigorous error bounds.
// This is a generic numerical-quadrature test, not a claim about the actual QWZ integrand.
const assert = require('node:assert/strict');
const TWO_PI = 2 * Math.PI;
const frequency = 64;
function integrand(x) { return Math.cos(TWO_PI * frequency * x); }
function midpoint(n, f = integrand) {
  if (!Number.isInteger(n) || n < 1) throw new RangeError('n must be positive integer');
  let sum = 0;
  for (let i = 0; i < n; i++) sum += f((i + 0.5) / n);
  return sum / n;
}
function run() {
  // Integral of cos(2*pi*k*x) from 0 to 1 equals 0 for any nonzero integer k.
  const exact = 0;
  const coarse = midpoint(16);
  const fine = midpoint(32);
  const difference = Math.abs(fine - coarse);
  const estimatedBound = (2 / 3) * difference;
  const actualFineError = Math.abs(fine - exact);
  assert.ok(Math.abs(coarse - 1) < 1e-12);
  assert.ok(Math.abs(fine - 1) < 1e-12);
  assert.ok(difference < 1e-12);
  assert.ok(actualFineError > 0.99999999);
  assert.ok(actualFineError > estimatedBound);
  // Smoothness C^infty and positivity of a separate gap do not prevent aliasing.
  console.log(JSON.stringify({
    example: 'f(x)=cos(2*pi*64*x) on [0,1]', smooth: true,
    coarse_midpoint_N16: coarse, fine_midpoint_N32: fine,
    adjacent_difference: difference,
    proposed_2D_over_3_bound: estimatedBound,
    true_integral: exact,
    actual_error_N32: actualFineError,
    certificate_valid: actualFineError <= estimatedBound,
  }, null, 2));
}
run();
