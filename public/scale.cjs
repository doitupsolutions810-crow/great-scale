/** CJS mirror of scale.js for node test runner */
const PHI = (1 + Math.sqrt(5)) / 2;
const PHI_INV = PHI - 1;
const CONE = PHI_INV * PHI_INV;
const RATE = 0.85;
const FIXED = 4.5;

function heat(h) { return h * (1 - h); }
/** Canonical reflection on R/9Z; boundary class 0 ≡ 9 and interior midpoint 4.5 are fixed. */
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
function twoCycles() { return [[1, 8], [2, 7], [3, 6], [4, 5]]; }
function fixedPoint() { return FIXED; }
/**
 * GS-LVII: circle-native contraction. Canonicalize to [0,9) before the
 * affine step so C(x+9n) = C(x) on the quotient R/9Z. The raw real-line
 * formula C_k(x)=4.5+k(x-4.5) fails quotient compatibility for |k|<1
 * (only integer k=0 works); projecting first is the minimal fix that
 * keeps |k|<1 convergence while making the fiber constant.
 */
function softContract(x, k = 0.5) {
  const m = ((x % 9) + 9) % 9;
  return FIXED + k * (m - FIXED);
}
/** Pure involution channel: 9 - x. Agrees with softContract only at 4.5. */
function softMap(x) { return 9 - x; }
function stressResidual(x) {
  const m = ((x % 9) + 9) % 9;
  return Math.abs(m - involution(m));
}
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
    this.x = start; this.k = k; this.tickMs = tickMs;
    this.t = 0; this.history = []; this.maxHistory = 200;
    this.timer = null; this.running = false;
  }
  tick() {
    this.x = softContract(this.x, this.k);
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
    this.running = true;
    this.timer = setInterval(() => this.tick(), this.tickMs);
  }
  stop() {
    this.running = false;
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
  }
  reset(start = 1) { this.stop(); this.x = start; this.t = 0; this.history = []; }
  snapshot() {
    return {
      schema: 'great-scale.descent/v0.5.0', running: this.running, t: this.t, x: this.x, k: this.k,
      nearFixed: Math.abs(this.x - FIXED) < 0.05, residual: stressResidual(this.x),
      historyLen: this.history.length, last: this.history[this.history.length - 1] || null,
    };
  }
}
const HYPOTHESIS = Object.freeze({
  id: 'great-scale.main',
  statements: [
    'S(h)=h(1-h) is identical to lattice tension T(B)=B(1-B)',
    'f(x)=(9-(x mod 9)) mod 9; fixed classes are 0≡9 on the boundary and 4.5 in the interior; integer two-cycles 1↔8,2↔7,3↔6,4↔5',
    'GS-LVII: soft contraction is circle-native — C(x)=4.5+k*((x mod 9)-4.5), |k|<1, fiber-constant on R/9Z; raw real-line affine fails quotient compatibility for non-integer k',
    'softMap(x)=9-x is the pure involution channel; softContract is the contraction channel; they agree only at the fixed point 4.5 — two channels, two meanings, one scalar shadow when unnamed',
    'Stress residual |x-f(x)| is a computational diagnostic, not a physical observable by itself; it is representation-invariant on the canonical representative',
    'Cone: Ψ = CONE + S never below CONE; λ may contract below CONE at low heat',
    'Never claim certainty — always another perspective',
  ],
});
module.exports = {
  PHI, PHI_INV, CONE, RATE, FIXED, heat, involution, modDist, involutionIdentity,
  twoCycles, fixedPoint, softContract, softMap, stressResidual, descentStep,
  stateAt, DescentEngine, HYPOTHESIS,
};