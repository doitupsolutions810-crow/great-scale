/** Great Scale laws + discrete involution — geometry v0.4.2 */
export const PHI = (1 + Math.sqrt(5)) / 2;
export const PHI_INV = PHI - 1;
/** Cone floor φ⁻² ≈ 0.382 — Ψ = CONE + S never below CONE */
export const CONE = PHI_INV * PHI_INV;
export const RATE = 0.85;
export const RESIDUAL_DIMS = [4, 3, 1];
export const FIXED = 4.5;

export function heat(h) {
  return h * (1 - h);
}

/**
 * Discrete involution on the ninefold circle: f(x) = (9 - (x mod 9)) mod 9.
 * 0 ≡ 9 on the circle; f(0)=0, f(1)=8, f(4.5)=4.5, f(9)=0.
 * Identity holds modularly: f(f(x)) ≡ x (mod 9).
 */
export function involution(x) {
  const m = ((x % 9) + 9) % 9;
  return (9 - m) % 9;
}

/** Modular distance on [0,9) circle */
export function modDist(a, b) {
  let d = Math.abs((((a - b) % 9) + 9) % 9);
  return Math.min(d, 9 - d);
}

/** Modular identity check: f(f(x)) ≡ x (mod 9) */
export function involutionIdentity(x) {
  return modDist(involution(involution(x)), x) < 1e-9;
}

export function twoCycles() {
  return [
    [1, 8],
    [2, 7],
    [3, 6],
    [4, 5],
  ];
}

/** Contraction target (not the full fixed set of the circle involution). */
export function fixedPoint() {
  return FIXED;
}

/** Fixed points of x ↦ −x mod 9 on the ninefold circle: 0 and 4.5. */
export function involutionFixedPoints() {
  return [0, 4.5];
}

/**
 * Soft contraction toward the contraction target x*=4.5.
 * |k| < 1 guarantees convergence. Default k=0.5.
 * This is the descent dynamics — not a blend with the involution
 * (which preserves distance from 4.5 and yields two-cycles).
 */
function canonicalizeCircleCoordinate(x) {
  if (!Number.isFinite(x)) throw new TypeError('circle coordinate must be finite');
  return ((x % 9) + 9) % 9;
}
function validateContractionFactor(k) {
  if (!Number.isFinite(k) || Math.abs(k) >= 1) throw new RangeError('contraction factor k must be finite and satisfy |k| < 1');
  return k;
}
export function softContract(x, k = 0.5) {
  if (!Number.isFinite(x)) throw new TypeError('contraction coordinate must be finite');
  validateContractionFactor(k);
  return FIXED + k * (x - FIXED);
}

/**
 * Linear involution shadow (exact reflection through 4.5).
 * g(g(x)) = x, g(4.5) = 4.5. The circle map f fixes [0] and [4.5]; 0 and 9 are equivalent representatives.
 */
export function softMap(x) {
  return 9 - x;
}

/**
 * Stress residual: distance between a point and its involution image.
 * Zero at both involution fixed points (0 and 4.5); maximal on two-cycle extremes.
 * Computational "moment of now" between continuous position and discrete structure.
 */
export function stressResidual(x) {
  return modDist(x, involution(x));
}

/** One descent step: soft contraction toward 4.5 */
export function descentStep(x, k = 0.5) {
  return softContract(x, k);
}

/**
 * Phase-time state. Ψ = CONE + S is the cone-respecting height;
 * λ = φ^(−n) is radial scale and may dip below CONE at low heat — that is allowed.
 */
export function stateAt(t, rate = RATE) {
  const phase = (t * rate) % 1;
  const h = 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
  const S = heat(h);
  const n = 8 - 4 * S;
  const lam = Math.pow(PHI, -n);
  const psi = CONE + S;
  const theta = 2 * Math.PI * phase;
  const eps = 0.12 * Math.sin(2 * theta);
  return {
    phase,
    h,
    S,
    n,
    lam,
    psi,
    fold: 0.8,
    zero_mode: PHI,
    xyz: [(1 + eps) * Math.cos(theta) * lam, 4 * S, (1 + eps) * Math.sin(theta) * lam],
  };
}

/** Background descent engine — contracts toward x*=4.5 */
export class DescentEngine {
  constructor({ start = 1, k = 0.5, tickMs = 150 } = {}) {
    this.x = canonicalizeCircleCoordinate(start);
    this.k = validateContractionFactor(k);
    this.tickMs = tickMs;
    this.t = 0;
    this.history = [];
    this.maxHistory = 200;
    this.timer = null;
    this.running = false;
  }

  tick() {
    this.x = softContract(canonicalizeCircleCoordinate(this.x), this.k);
    this.t += 1;
    const rec = {
      t: this.t,
      x: this.x,
      S: heat(this.x / 9),
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

  reset(start = 1) {
    this.stop();
    this.x = canonicalizeCircleCoordinate(start);
    this.t = 0;
    this.history = [];
  }

  snapshot() {
    return {
      schema: 'great-scale.descent/v0.4.2',
      running: this.running,
      t: this.t,
      x: this.x,
      k: this.k,
      nearFixed: Math.abs(this.x - FIXED) < 0.05,
      residual: stressResidual(this.x),
      historyLen: this.history.length,
      last: this.history[this.history.length - 1] || null,
    };
  }
}

export const HYPOTHESIS = Object.freeze({
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

export default {
  PHI,
  CONE,
  FIXED,
  heat,
  involution,
  twoCycles,
  fixedPoint,
  involutionFixedPoints,
  softMap,
  softContract,
  stressResidual,
  descentStep,
  stateAt,
  DescentEngine,
  HYPOTHESIS,
};
