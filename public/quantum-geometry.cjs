/**
 * Additive QGT → Great Scale bridge.
 * Inputs use F_12 = 2 Im(Q_12). Existing stateAt() dynamics are unchanged.
 */
const { PHI, CONE, heat } = require('./scale.cjs');
// Error-free transforms recover low product bits before subtracting nearly equal terms.
// Inputs are normalized to |x| <= 1, keeping Dekker splitting away from overflow.
function twoProduct(a, b) {
  const product = a * b;
  const splitter = 134217729;
  const ca = splitter * a, cb = splitter * b;
  const aHi = ca - (ca - a), bHi = cb - (cb - b);
  const aLo = a - aHi, bLo = b - bHi;
  const error = ((aHi * bHi - product) + aHi * bLo + aLo * bHi) + aLo * bLo;
  return [product, error];
}
function twoDiff(a, b) {
  const value = a - b, bVirtual = a - value, aVirtual = value + bVirtual;
  return [value, (a - aVirtual) + (bVirtual - b)];
}
function twoSum(a, b) {
  const value = a + b, bVirtual = value - a, aVirtual = value - bVirtual;
  return [value, (a - aVirtual) + (b - bVirtual)];
}
function compensatedDeterminant2x2(a11, a12, a22) {
  const [p, pError] = twoProduct(a11, a22);
  const [q, qError] = twoProduct(a12, a12);
  const [difference, differenceError] = twoDiff(p, q);
  const [productErrorDifference, productErrorDifferenceError] = twoDiff(pError, qError);
  const [high, low] = twoSum(difference, productErrorDifference);
  return high + (low + differenceError + productErrorDifferenceError);
}
function quantumGeometryBridge({ g11, g12, g22, curvature }, tolerance = 1e-10) {
  const values = [g11, g12, g22, curvature];
  if (!values.every(Number.isFinite)) throw new TypeError('Metric entries and curvature must be finite numbers.');
  if (!(tolerance >= 0) || !Number.isFinite(tolerance)) throw new TypeError('Tolerance must be finite and nonnegative.');
  if (!(g11 > 0) || !(g22 > 0)) throw new RangeError('Metric diagonal entries must be positive.');
  // Normalize the metric before determinant arithmetic. Under a common positive
  // rescaling (g,F) -> (s g,s F), chi is invariant, but raw determinants may
  // underflow/overflow even when normalized geometry remains representable.
  const metricMagnitude = Math.max(g11, Math.abs(g12), g22);
  // Use a power-of-two scale: division by an arbitrary maximum can round
  // each entry before determinant evaluation and erase relative information
  // in an ill-conditioned matrix. Binary exponent scaling is exact for
  // normal binary64 values and keeps Dekker splitting away from overflow.
  const metricScale = Math.pow(2, Math.floor(Math.log2(metricMagnitude)));
  const a11 = g11 / metricScale, a12 = g12 / metricScale, a22 = g22 / metricScale;
  const detScaled = compensatedDeterminant2x2(a11, a12, a22);
  if (!(detScaled > 0) || !Number.isFinite(detScaled)) throw new RangeError('The two-direction metric must be positive and nondegenerate (scaled detG > 0).');
  const scaledCurvature = curvature / metricScale;
  const rawChi = Math.abs(scaledCurvature) / (2 * Math.sqrt(detScaled));
  if (!Number.isFinite(rawChi) || rawChi > 1 + tolerance) throw new RangeError('QGT positivity violated: |F_12| > 2 sqrt(detG).');
  // Preserve evidence of tolerated clipping: otherwise a slightly invalid input
  // is indistinguishable from exact geometric saturation in downstream scalars.
  const positivityOvershoot = Math.max(0, rawChi - 1);
  const saturationProjected = rawChi > 1;
  const chi = Math.min(1, rawChi);
  const detQScaled = Math.max(0, detScaled - (scaledCurvature * scaledCurvature) / 4);
  // Raw determinants may be outside binary64's representable range even
  // when normalized geometry and eigenvalues remain useful. Never return
  // Infinity or silently conflate a positive underflowed determinant with 0.
  function exposeRawDeterminant(normalizedDeterminant) {
    const raw = (normalizedDeterminant * metricScale) * metricScale;
    if (!Number.isFinite(raw)) return { value: null, status: 'overflow' };
    if (normalizedDeterminant > 0 && raw === 0) return { value: null, status: 'underflow' };
    return { value: raw, status: 'finite' };
  }
  const detGResult = exposeRawDeterminant(detScaled);
  const detQResult = exposeRawDeterminant(detQScaled);
  const detG = detGResult.value;
  const detQ = detQResult.value;
  const relativeResidual = Math.max(0, 1 - chi * chi);
  const hQuantum = (1 + chi) / 2;
  const SQuantum = heat(hQuantum);
  const psiQuantum = CONE + SQuantum;
  // Compute eigenvalues in normalized coordinates first. Raw sums and squares
  // can overflow even when the rescaled eigenvalues themselves are representable.
  const metricMeanScaled = (a11 + a22) / 2;
  const metricSpreadScaled = Math.hypot((a11 - a22) / 2, a12);
  const lambdaMaxScaled = metricMeanScaled + metricSpreadScaled;
  // Obtain the small eigenvalue from det/lambda_max, not mean - spread,
  // which subtracts nearly equal values near metric degeneracy.
  const lambdaMinScaled = detScaled / lambdaMaxScaled;
  const metricEigenvalues = [lambdaMinScaled * metricScale, lambdaMaxScaled * metricScale];
  const metricConditionNumber = lambdaMaxScaled / lambdaMinScaled;
  const relativeEigenvalue = lambdaMinScaled / lambdaMaxScaled;
  const metricConditionStatus = !Number.isFinite(metricConditionNumber) || relativeEigenvalue <= 64 * Number.EPSILON
    ? 'numerically-unresolved'
    : metricConditionNumber > 1 / Math.sqrt(Number.EPSILON)
      ? 'ill-conditioned'
      : 'well-conditioned';
  const nQuantum = 8 - 4 * SQuantum;
  return {
    schema: 'great-scale.quantum-geometry/v1',
    detG, detQ, detGStatus: detGResult.status, detQStatus: detQResult.status,
    signedCurvature: curvature, metricEigenvalues,
    metricAnisotropy: metricEigenvalues[0] / metricEigenvalues[1],
    metricConditionNumber, metricConditionStatus,
    curvatureFraction: chi, rawCurvatureFraction: rawChi, positivityOvershoot, saturationProjected,
    hQuantum, SQuantum, relativeResidual, psiQuantum,
    nQuantum, lambdaQuantum: Math.pow(PHI, -nQuantum)
  };
}
module.exports = { quantumGeometryBridge };
