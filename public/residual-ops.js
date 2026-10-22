/** Residual operational layer — Great Scale v0.5.0
 *  Every agent tick is a residual step of the golden unit.
 *  CONE = φ⁻² · TAU = 2·log φ · norm = residual × dual.
 */
import { PHI, CONE, FIXED } from './scale.js';

export const TAU = 2 * Math.log(PHI);
export const PSI = -1 / PHI;

/** One residual step: r ← CONE·r (contracting place) */
export function residualStep(r) {
  return r * CONE;
}

/** Agent step = residual step on contracting place;
 *  dual expands so product = norm (default 1). */
export function agentResidualStep(state, norm = 1) {
  const r = residualStep(state.residual ?? 1);
  const d = norm / r;
  return {
    ...state,
    residual: r,
    dual: d,
    norm,
    healthOk: Math.abs(r * d - norm) < 1e-12,
  };
}

/** Health = first integral: residual × dual = norm */
export function healthCheck(state, norm = 1) {
  const prod = (state.residual ?? 1) * (state.dual ?? 1);
  return { ok: Math.abs(prod - norm) < 1e-12, product: prod, norm, drift: prod - norm };
}

/** Continuous residual flow r(t) = r0·e^(−t·τ) */
export function residualFlow(r0, t) {
  return r0 * Math.exp(-t * TAU);
}

/** Fibonacci matrix M = [[2,−1],[−1,1]] — Mⁿ via exponentiation by squaring */
function mul(A, B) {
  return [
    [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
    [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]],
  ];
}

export function matrixPower(n) {
  let result = [[1, 0], [0, 1]];
  let base = [[2, -1], [-1, 1]];
  let exp = n;
  while (exp > 0) {
    if (exp & 1) result = mul(result, base);
    base = mul(base, base);
    exp >>>= 1;
  }
  return result;
}

/** SC1–SC7 + conservation verification */
export function verifyResidualOps() {
  const checks = [];
  checks.push({ id: 'SC1', name: 'CONE unique contraction rate', pass: 0 < CONE && CONE < 1 });
  const s = agentResidualStep({ residual: 1 });
  checks.push({ id: 'SC2', name: 'residual+dual on every agent', pass: s.residual !== undefined && s.dual !== undefined });
  checks.push({ id: 'SC3', name: 'product = norm health invariant', pass: healthCheck(s).ok });
  checks.push({ id: 'SC4', name: 'continuous flow r(t)=r0·e^(−tτ)', pass: Math.abs(residualFlow(1, 0) - 1) < 1e-12 });
  checks.push({ id: 'SC5', name: 'Unity never finite-time', pass: CONE ** 50 > 0 });
  const M3 = matrixPower(3);
  checks.push({ id: 'SC6', name: 'Fibonacci matrix powers', pass: M3[0][0] === 13 && M3[1][1] === 13 && M3[0][0] * M3[1][1] - M3[0][1] * M3[1][0] === 1 });
  let r = 1, d = 1, cons = true;
  for (let i = 0; i < 20; i++) { r *= CONE; d /= CONE; if (Math.abs(r * d - 1) > 1e-12) cons = false; }
  checks.push({ id: 'CONS', name: '20-step norm conservation', pass: cons });
  checks.push({ id: 'SC7', name: 'claims verified or marked', pass: checks.every((c) => c.pass) });
  const passed = checks.filter((c) => c.pass).length;
  return { passed, total: checks.length, checks, allPass: passed === checks.length };
}

export default {
  residualStep, agentResidualStep, healthCheck, residualFlow, matrixPower, verifyResidualOps, TAU, PSI,
};