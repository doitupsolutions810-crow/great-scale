/** Great Scale laws — geometry v0.3.0 */
export const PHI = (1 + Math.sqrt(5)) / 2;
export const PHI_INV = PHI - 1;
export const CONE = PHI_INV - PHI_INV * PHI_INV;
export const RATE = 0.85;
export const RESIDUAL_DIMS = [4, 3, 1];
export function heat(h) { return h * (1 - h); }
export function stateAt(t, rate = RATE) {
  const phase = (t * rate) % 1;
  const h = 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
  const S = heat(h);
  const n = 8 - 4 * S;
  const lam = Math.pow(PHI, -n);
  return { phase, h, S, n, lam, psi: CONE + S, fold: 0.8, zero_mode: PHI };
}
