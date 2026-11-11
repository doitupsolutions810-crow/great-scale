/**
 * Bidirectional QGT ↔ Descent bridge (v0.5.8)
 *
 * Forward  : quantumGeometryBridge  (metric + curvature → Scale scalars)
 * Reverse  : descentToQuantumSeed   (descent state → χ seed + metric seed)
 * Roundtrip: coupleDescentWithQGT   (closed loop with CONE + residual checks)
 *
 * Stance: measured coherence only. No certainty claimed.
 */
'use strict';

const {
  PHI, CONE, FIXED, heat, softContract, stressResidual, modDist, stateAt,
} = require('./scale.cjs');
const { quantumGeometryBridge } = require('./quantum-geometry.cjs');

/**
 * Map a descent state into a QGT-positive seed.
 *
 * Design choices (explicit, revisable):
 * - χ_implied grows with modular distance to FIXED and with stress residual,
 *   saturating in [0,1]. Near FIXED ⇒ χ≈0 (flat geometry).
 * - Metric seed is a simple SPD pair whose anisotropy tracks residual energy.
 * - Curvature is chosen so that the forward bridge recovers χ_implied
 *   (up to clipping at the positivity boundary).
 */
function descentToQuantumSeed({
  x,
  t = 0,
  rate = 0.85,
  baseScale = 1.0,
} = {}) {
  if (!Number.isFinite(x)) throw new TypeError('x must be finite');
  if (!Number.isFinite(baseScale) || baseScale <= 0) {
    throw new RangeError('baseScale must be positive and finite');
  }

  const m = ((x % 9) + 9) % 9;
  const dist = modDist(m, FIXED);
  const stress = stressResidual(x);
  const st = stateAt(t, rate);
  const distNorm = Math.min(1, dist / 4.5);
  const stressNorm = Math.min(1, stress / 9);
  const heatNorm = Math.min(1, st.S / 0.25);
  const chiImplied = Math.min(1, 0.5 * distNorm + 0.3 * stressNorm + 0.2 * heatNorm);

  const aniso = 1 + 0.5 * stressNorm;
  const g11 = baseScale * aniso;
  const g22 = baseScale / aniso;
  const g12 = 0;
  const detG = g11 * g22;
  const curvature = chiImplied * 2 * Math.sqrt(detG);

  return {
    schema: 'great-scale.descent-to-qgt/v0.5.8',
    x, m, dist, stress,
    phase: st.phase,
    S_state: st.S,
    psi_state: st.psi,
    chiImplied,
    metricSeed: { g11, g12, g22, curvature },
    forward: null,
  };
}

/**
 * Closed coupling: descent state → QGT seed → forward scalars → modulated k → next x.
 */
function coupleDescentWithQGT({
  x,
  t = 0,
  rate = 0.85,
  kBase = 0.5,
  baseScale = 1.0,
  steps = 1,
} = {}) {
  const history = [];
  let curX = x;
  let curT = t;

  for (let i = 0; i < steps; i++) {
    const seed = descentToQuantumSeed({
      x: curX, t: curT, rate, baseScale,
    });
    const qgt = quantumGeometryBridge(seed.metricSeed);
    const k = Math.max(
      0.12,
      Math.min(0.92, kBase * (1 - 0.35 * qgt.SQuantum * 4))
    );
    const nextX = softContract(curX, k);
    const rec = {
      step: i,
      x: curX,
      nextX,
      k,
      chiImplied: seed.chiImplied,
      chiForward: qgt.curvatureFraction,
      SQuantum: qgt.SQuantum,
      psiQuantum: qgt.psiQuantum,
      psiState: seed.psi_state,
      residual: stressResidual(curX),
      residualNext: stressResidual(nextX),
      dist: seed.dist,
      coneFloorOk: qgt.psiQuantum + 1e-14 >= CONE,
      stateConeOk: seed.psi_state + 1e-14 >= CONE,
    };
    history.push(rec);
    curX = nextX;
    curT += 1;
  }

  return {
    schema: 'great-scale.qgt-descent-couple/v0.5.8',
    finalX: curX,
    finalT: curT,
    history,
    allConeOk: history.every(r => r.coneFloorOk && r.stateConeOk),
    meanChi: history.reduce((a, r) => a + r.chiForward, 0) / history.length,
    meanResidual: history.reduce((a, r) => a + r.residualNext, 0) / history.length,
  };
}

function roundTripChi(x, t = 0, tol = 1e-9) {
  const seed = descentToQuantumSeed({ x, t });
  const qgt = quantumGeometryBridge(seed.metricSeed);
  const err = Math.abs(qgt.curvatureFraction - seed.chiImplied);
  return {
    chiImplied: seed.chiImplied,
    chiForward: qgt.curvatureFraction,
    err,
    ok: err <= tol + 1e-12,
    psiQuantum: qgt.psiQuantum,
    coneOk: qgt.psiQuantum + 1e-14 >= CONE,
  };
}

module.exports = {
  descentToQuantumSeed,
  coupleDescentWithQGT,
  roundTripChi,
  quantumGeometryBridge,
};
