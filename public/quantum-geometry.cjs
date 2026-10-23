/**
 * Additive QGT → Great Scale bridge.
 * Inputs use F_12 = 2 Im(Q_12). Existing stateAt() dynamics are unchanged.
 */
const { PHI, CONE, heat } = require('./scale.cjs');
function quantumGeometryBridge({ g11, g12, g22, curvature }, tolerance = 1e-10) {
  const values = [g11, g12, g22, curvature];
  if (!values.every(Number.isFinite)) throw new TypeError('Metric entries and curvature must be finite numbers.');
  if (!(tolerance >= 0) || !Number.isFinite(tolerance)) throw new TypeError('Tolerance must be finite and nonnegative.');
  // A real symmetric 2×2 metric is positive definite iff g11 > 0 and detG > 0.
  if (!(g11 > 0) || !(g22 > 0)) throw new RangeError('Metric diagonal entries must be positive.');
  const detG = g11 * g22 - g12 * g12;
  if (!(detG > 0)) throw new RangeError('The two-direction metric must be positive and nondegenerate (detG > 0).');
  const rawChi = Math.abs(curvature) / (2 * Math.sqrt(detG));
  if (rawChi > 1 + tolerance) throw new RangeError('QGT positivity violated: |F_12| > 2 sqrt(detG).');
  const chi = Math.min(1, rawChi);
  // Round-off excursions within tolerance must not expose a negative Gram determinant.
  const detQ = Math.max(0, detG - (curvature * curvature) / 4);
  const relativeResidual = Math.max(0, 1 - chi * chi);
  const hQuantum = (1 + chi) / 2;
  const SQuantum = heat(hQuantum);
  const psiQuantum = CONE + SQuantum;
  const nQuantum = 8 - 4 * SQuantum;
  const lambdaQuantum = Math.pow(PHI, -nQuantum);
  return { schema: 'great-scale.quantum-geometry/v1', detG, detQ, curvatureFraction: chi, hQuantum, SQuantum, relativeResidual, psiQuantum, nQuantum, lambdaQuantum };
}
module.exports = { quantumGeometryBridge };
