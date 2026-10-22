(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.GreatScaleDescent = api;
})(typeof globalThis === 'undefined' ? this : globalThis, function () {
  function computeRobustDescentCertificate({ initialResidual, k, disturbanceBound, steps } = {}) {
    if (!Number.isFinite(initialResidual) || initialResidual < 0 || initialResidual > 7) {
      throw new RangeError('initialResidual must be within [0, 7] on the configured [1, 8] chart');
    }
    if (!Number.isFinite(k) || Math.abs(k) >= 1) {
      throw new RangeError('k must be finite and satisfy |k| < 1');
    }
    if (!Number.isFinite(disturbanceBound) || disturbanceBound < 0) {
      throw new RangeError('disturbanceBound must be non-negative and finite');
    }
    if (!Number.isSafeInteger(steps) || steps < 0) {
      throw new RangeError('steps must be a non-negative safe integer');
    }

    const contraction = Math.abs(k);
    const contractionPower = steps === 0 ? 1 : contraction ** steps;
    const geometricSum = steps === 0
      ? 0
      : -Math.expm1(steps * Math.log(contraction)) / (1 - contraction);
    const recurrenceBound = contractionPower * initialResidual + 2 * disturbanceBound * geometricSum;
    const residualUpperBound = Math.min(7, recurrenceBound);
    const ultimateResidualUpperBound = Math.min(7, 2 * disturbanceBound / (1 - contraction));

    return {
      steps,
      contraction,
      disturbanceBound,
      residualUpperBound,
      normalizedResidualUpperBound: residualUpperBound / 7,
      ultimateResidualUpperBound,
      normalizedUltimateResidualUpperBound: ultimateResidualUpperBound / 7,
      domain: [1, 8],
      projectionRequired: true,
      status: 'conditional bounded-disturbance certificate',
    };
  }

  return { computeRobustDescentCertificate };
});
