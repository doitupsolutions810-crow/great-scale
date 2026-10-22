/** CJS mirror of scale.js for node test runner */
const PHI = (1 + Math.sqrt(5)) / 2;
const PHI_INV = PHI - 1;
const CONE = PHI_INV * PHI_INV;
const RATE = 0.85;
const FIXED = 4.5;

function heat(h) { return h * (1 - h); }
function involution(x) {
  const m = ((x % 9) + 9) % 9;
  return (9 - m) % 9;
}
function modDist(a, b) {
  let d = Math.abs((((a - b) % 9) + 9) % 9);
  return Math.min(d, 9 - d);
}
function involutionIdentity(x) {
  return modDist(involution(involution(x)), x) < 1e-9;
}
function twoCycles() {
  return [[1, 8], [2, 7], [3, 6], [4, 5]];
}
// Contraction target; the circle involution has fixed points 0 and 4.5.
function fixedPoint() { return FIXED; }
function involutionFixedPoints() { return [0, 4.5]; }
function canonicalizeCircleCoordinate(x) {
  if (!Number.isFinite(x)) throw new TypeError('circle coordinate must be finite');
  return ((x % 9) + 9) % 9;
}
function validateContractionFactor(k) {
  if (!Number.isFinite(k) || Math.abs(k) >= 1) throw new RangeError('contraction factor k must be finite and satisfy |k| < 1');
  return k;
}
function validateTickInterval(tickMs) {
  // Keep timer delays inside the portable signed-32-bit millisecond range.
  if (!Number.isFinite(tickMs) || tickMs < 1 || tickMs > 2147483647) {
    throw new RangeError('tickMs must be finite and in [1, 2147483647] milliseconds');
  }
  return tickMs;
}
function softContract(x, k = 0.5) {
  if (!Number.isFinite(x)) throw new TypeError('contraction coordinate must be finite');
  validateContractionFactor(k);
  return FIXED + k * (x - FIXED);
}
// Real-line reflection; on the circle, 0 and 9 are equivalent.
function softMap(x) { return 9 - x; }
// Zero at both circle-involution fixed points: 0 and 4.5.
function stressResidual(x) { return modDist(x, involution(x)); }
function descentStep(x, k = 0.5) { return softContract(x, k); }
function stateAt(t, rate = RATE) {
  const phase = (t * rate) % 1;
  const h = 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
  const S = heat(h);
  const n = 8 - 4 * S;
  const lam = Math.pow(PHI, -n);
  const psi = CONE + S;
  const theta = 2 * Math.PI * phase;
  const eps = 0.12 * Math.sin(2 * theta);
  return {
    phase, h, S, n, lam, psi, fold: 0.8, zero_mode: PHI,
    xyz: [(1 + eps) * Math.cos(theta) * lam, 4 * S, (1 + eps) * Math.sin(theta) * lam],
  };
}
class DescentEngine {
  constructor({ start = 1, k = 0.5, tickMs = 150 } = {}) {
    this.x = canonicalizeCircleCoordinate(start); this.k = validateContractionFactor(k); this.tickMs = validateTickInterval(tickMs);
    this.t = 0; this.history = []; this.maxHistory = 200;
    this.timer = null; this.running = false;
  }
  tick() {
    this.x = softContract(canonicalizeCircleCoordinate(this.x), this.k);
    this.t += 1;
    const rec = {
      t: this.t, x: this.x, S: heat(this.x / 9),
      residual: stressResidual(this.x),
      nearFixed: Math.abs(this.x - FIXED) < 0.05,
      involution: involution(this.x),
    };
    this.history.push(rec);
    if (this.history.length > this.maxHistory) this.history.shift();
    return rec;
  }
  start() {
    if (this.running) return;
    const tickMs = validateTickInterval(this.tickMs); // Revalidate because the field is publicly mutable.
    this.timer = setInterval(() => this.tick(), tickMs);
    this.running = true;
  }
  stop() {
    this.running = false;
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
  }
  reset(start = 1) {
    this.stop(); this.x = canonicalizeCircleCoordinate(start); this.t = 0; this.history = [];
  }
  snapshot() {
    return {
      schema: 'great-scale.descent/v0.4.2',
      running: this.running, t: this.t, x: this.x, k: this.k,
      nearFixed: Math.abs(this.x - FIXED) < 0.05,
      residual: stressResidual(this.x),
      historyLen: this.history.length,
      last: this.history[this.history.length - 1] || null,
    };
  }
}
const HYPOTHESIS = Object.freeze({
  id: 'great-scale.main',
  statements: [
    'S(h)=h(1-h) is identical to lattice tension T(B)=B(1-B)',
    'f(x)=(9-(x mod 9)) mod 9 has circle fixed points 0 and 4.5, plus two-cycles 1↔8,2↔7,3↔6,4↔5',
    'Soft contraction x′=4.5+k(x−4.5), |k|<1, converges to contraction target 4.5',
    'Stress residual is the circular distance d₉(x,f(x)); interpret it on the ninefold circle',
    'Cone: Ψ = CONE + S never below CONE; λ may contract below CONE at low heat',
    'Never claim certainty — always another perspective',
  ],
});
module.exports = {
  PHI, PHI_INV, CONE, RATE, FIXED, heat, involution, modDist, involutionIdentity,
  twoCycles, fixedPoint, involutionFixedPoints, softContract, softMap, stressResidual, descentStep,
  stateAt, DescentEngine, HYPOTHESIS,
};
