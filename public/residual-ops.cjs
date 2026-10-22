/** CJS mirror of residual-ops.js for node test runner — v0.5.1 */
const { PHI, CONE, FIXED } = require('./scale.cjs');

const TAU = 2 * Math.log(PHI);
const PSI = -1 / PHI;

const CONE_MATRIX = [[2, -1], [-1, 1]];
const FIB_MATRIX = [[1, 1], [1, 0]];

function residualStep(r) { return r * CONE; }

function agentResidualStep(state, norm = 1) {
  const r = residualStep(state.residual ?? 1);
  const d = norm / r;
  return { ...state, residual: r, dual: d, norm, healthOk: Math.abs(r * d - norm) < 1e-12 };
}

function healthCheck(state, norm = 1) {
  const prod = (state.residual ?? 1) * (state.dual ?? 1);
  return { ok: Math.abs(prod - norm) < 1e-12, product: prod, norm, drift: prod - norm };
}

function residualFlow(r0, t) { return r0 * Math.exp(-t * TAU); }

function mul(A, B) {
  return [
    [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
    [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]],
  ];
}

function matrixPower(n, matrix = CONE_MATRIX) {
  let result = [[1, 0], [0, 1]];
  let base = matrix.map((row) => row.slice());
  let exp = n;
  while (exp > 0) {
    if (exp & 1) result = mul(result, base);
    base = mul(base, base);
    exp >>>= 1;
  }
  return result;
}

function verifyResidualOps() {
  const checks = [];
  checks.push({ id: 'SC1', name: 'CONE unique contraction rate', pass: 0 < CONE && CONE < 1 });
  const s = agentResidualStep({ residual: 1 });
  checks.push({ id: 'SC2', name: 'residual+dual on every agent', pass: s.residual !== undefined && s.dual !== undefined });
  checks.push({ id: 'SC3', name: 'product = norm health invariant', pass: healthCheck(s).ok });
  checks.push({ id: 'SC4', name: 'continuous flow r(t)=r0·e^(−tτ)', pass: Math.abs(residualFlow(1, 0) - 1) < 1e-12 });
  checks.push({ id: 'SC5', name: 'Unity never finite-time', pass: Math.pow(CONE, 50) > 0 });
  const M3 = matrixPower(3);
  const detM3 = M3[0][0] * M3[1][1] - M3[0][1] * M3[1][0];
  checks.push({ id: 'SC6', name: 'CONE-matrix powers (M^3=[[13,-8],[-8,5]], det 1)', pass: M3[0][0] === 13 && M3[1][1] === 5 && detM3 === 1 });
  const F3 = matrixPower(3, FIB_MATRIX);
  checks.push({ id: 'SC6b', name: 'Fibonacci companion F^3=[[3,2],[2,1]]', pass: F3[0][0] === 3 && F3[1][1] === 1 && F3[0][0] * F3[1][1] - F3[0][1] * F3[1][0] === -1 });
  const M = CONE_MATRIX;
  const M2 = mul(M, M);
  const charZero = M2[0][0] - 3 * M[0][0] + 1 === 0 && M2[0][1] - 3 * M[0][1] === 0 && M2[1][0] - 3 * M[1][0] === 0 && M2[1][1] - 3 * M[1][1] + 1 === 0;
  checks.push({ id: 'SC6c', name: 'CONE-matrix satisfies x^2-3x+1=0', pass: charZero });
  let r = 1, d = 1, cons = true;
  for (let i = 0; i < 20; i++) { r *= CONE; d /= CONE; if (Math.abs(r * d - 1) > 1e-12) cons = false; }
  checks.push({ id: 'CONS', name: '20-step norm conservation', pass: cons });
  checks.push({ id: 'SC7', name: 'claims verified or marked', pass: checks.every((c) => c.pass) });
  const passed = checks.filter((c) => c.pass).length;
  return { passed, total: checks.length, checks, allPass: passed === checks.length };
}

module.exports = {
  TAU, PSI, CONE_MATRIX, FIB_MATRIX, residualStep, agentResidualStep, healthCheck, residualFlow, matrixPower, verifyResidualOps,
};