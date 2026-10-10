/* Great Scale phase-time camera atlas — scale-generated navigation */
export const PHI = (1 + Math.sqrt(5)) / 2;
export const CONE = (PHI - 1) - (PHI - 1) ** 2;
export const VIEW_PRESETS = {
  Watch: { az: 35, el: 25 },
  Observer: { az: 0, el: 80 },
  Forward: { az: 90, el: 15 },
  Adjacent: { az: -40, el: 20 },
  Down: { az: 0, el: -55 },
};
export function heat(h) { return h * (1 - h); }
export function phaseXYZ(phase, S) {
  const th = 2 * Math.PI * phase;
  const r = 1 + 0.12 * Math.sin(th * 2);
  return [r * Math.cos(th), S * 3.5, r * Math.sin(th)];
}
export function project3(x, y, z, camAz, camEl, camDist, W, H) {
  const az = (camAz * Math.PI) / 180, el = (camEl * Math.PI) / 180;
  let x1 = x * Math.cos(az) - z * Math.sin(az);
  let z1 = x * Math.sin(az) + z * Math.cos(az);
  let y1 = y * Math.cos(el) - z1 * Math.sin(el);
  let z2 = y * Math.sin(el) + z1 * Math.cos(el);
  const f = (320 * camDist) / (2.5 + z2);
  return [W * 0.42 + x1 * f, H * 0.48 - y1 * f, z2];
}
export const LAWS = [
  'keep the mean',
  'respect residual partition 4+3+1',
  'Ψ never below cone',
  'only add scale-generated geometry',
];
