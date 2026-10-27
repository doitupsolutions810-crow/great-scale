'use strict';

const { CONE, heat } = require('../public/scale.cjs');

const TWO_PI = 2 * Math.PI;
const EPS = 1e-12;
function binaryEntropyNats(probability) {
  const p = Math.max(0, Math.min(1, probability));
  const left = p > 0 ? -p * Math.log(p) : 0;
  const right = p < 1 ? -(1 - p) * Math.log1p(-p) : 0;
  return left + right;
}
function complex(re, im = 0) { return [re, im]; }
function complexAdd(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
function complexMul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
function complexConjugate(a) { return [a[0], -a[1]]; }
function complexAbs(a) { return Math.hypot(a[0], a[1]); }

/** Qi-Wu-Zhang two-band Hamiltonian d(k)·sigma, lower-band eigenvector. */
function qiWuZhangLowerBandState(kx, ky, m) {
  const dx = Math.sin(kx), dy = Math.sin(ky), dz = m + Math.cos(kx) + Math.cos(ky);
  const energy = Math.hypot(dx, dy, dz);
  if (energy < EPS) throw new RangeError(`Band gap closes at (${kx}, ${ky}) for m=${m}.`);
  let a, b;
  if (dz >= 0) {
    const bReal = Math.sqrt((1 + dz / energy) / 2);
    a = complex((-dx / energy) / (2 * bReal), (dy / energy) / (2 * bReal));
    b = complex(bReal);
  } else {
    const aReal = Math.sqrt((1 - dz / energy) / 2);
    a = complex(aReal);
    b = complex((-dx / energy) / (2 * aReal), (-dy / energy) / (2 * aReal));
  }
  return [a, b];
}
function overlap(u, v) {
  return complexAdd(complexMul(complexConjugate(u[0]), v[0]), complexMul(complexConjugate(u[1]), v[1]));
}
function normalizedPhase(z) {
  const magnitude = complexAbs(z);
  if (magnitude < EPS) throw new RangeError('Neighboring occupied states have vanishing overlap; refine or inspect the grid.');
  return [z[0] / magnitude, z[1] / magnitude];
}

/**
 * Discrete Chern number using the gauge-invariant Fukui-Hatsugai-Suzuki plaquette phase.
 * Orientation: kx first, ky second; plaquette = arg(Ux Uy_x Ux_y* Uy*).
 */
function qiWuZhangChernNumber(m, gridSize = 40) {
  if (!Number.isFinite(m)) throw new TypeError('Mass parameter m must be finite.');
  if (Math.abs(m + 2) < EPS || Math.abs(m) < EPS || Math.abs(m - 2) < EPS) {
    throw new RangeError('Band gap closes at a topological phase boundary for m=' + m + '.');}
  if (!Number.isInteger(gridSize) || gridSize < 4) throw new RangeError('gridSize must be an integer >= 4.');
  const states = Array.from({ length: gridSize }, (_, i) =>
    Array.from({ length: gridSize }, (_, j) =>
      qiWuZhangLowerBandState(TWO_PI * i / gridSize, TWO_PI * j / gridSize, m)));
  const ux = Array.from({ length: gridSize }, () => Array(gridSize));
  const uy = Array.from({ length: gridSize }, () => Array(gridSize));
  for (let i = 0; i < gridSize; i++) for (let j = 0; j < gridSize; j++) {
    ux[i][j] = normalizedPhase(overlap(states[i][j], states[(i + 1) % gridSize][j]));
    uy[i][j] = normalizedPhase(overlap(states[i][j], states[i][(j + 1) % gridSize]));
  }
  let phaseSum = 0;
  for (let i = 0; i < gridSize; i++) for (let j = 0; j < gridSize; j++) {
    const plaquette = complexMul(
      complexMul(complexMul(ux[i][j], uy[(i + 1) % gridSize][j]), complexConjugate(ux[i][(j + 1) % gridSize])),
      complexConjugate(uy[i][j]));
    phaseSum += Math.atan2(plaquette[1], plaquette[0]);
  }
  return phaseSum / TWO_PI;
}

/** Analytic local QGT of n=d/|d| at a regular point; curvature sign follows this code's orientation. */
function qiWuZhangLocalQGT(kx, ky, m) {
  const d = [Math.sin(kx), Math.sin(ky), m + Math.cos(kx) + Math.cos(ky)];
  const energy = Math.hypot(...d);
  if (energy < EPS) throw new RangeError(`Band gap closes at (${kx}, ${ky}) for m=${m}.`);
  const n = d.map(v => v / energy);
  const dx = [Math.cos(kx), 0, -Math.sin(kx)], dy = [0, Math.cos(ky), -Math.sin(ky)];
  const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const projectDerivative = v => v.map((x, i) => (x - n[i] * dot(n, v)) / energy);
  const nx = projectDerivative(dx), ny = projectDerivative(dy);
  return {
    g11: dot(nx, nx) / 4, g12: dot(nx, ny) / 4, g22: dot(ny, ny) / 4,
    curvature: -dot(n, cross(nx, ny)) / 2, gap: 2 * energy
  };
}
/**
 * Uniform-grid whole-Brillouin-zone QGT integrals.
 * offset=0 samples grid vertices; offset=0.5 samples cell centers.
 */
function qiWuZhangLocalIntegrals(m, gridSize, offset = 0.5) {
  const dk = TWO_PI / gridSize;
  let signedCurvature = 0, absoluteCurvature = 0, metricAreaDensity = 0;
  let positiveCurvature = 0, negativeCurvature = 0;
  for (let i = 0; i < gridSize; i++) for (let j = 0; j < gridSize; j++) {
    const kx = TWO_PI * (i + offset) / gridSize;
    const ky = TWO_PI * (j + offset) / gridSize;
    const q = qiWuZhangLocalQGT(kx, ky, m);
    signedCurvature += q.curvature;
    absoluteCurvature += Math.abs(q.curvature);
    if (q.curvature >= 0) positiveCurvature += q.curvature;
    else negativeCurvature += -q.curvature;
    metricAreaDensity += Math.sqrt(Math.max(0, q.g11 * q.g22 - q.g12 * q.g12));
  }
  const cellArea = dk * dk;
  return {
    integratedCurvature: signedCurvature * cellArea / TWO_PI,
    absoluteCurvatureBudget: absoluteCurvature * cellArea / TWO_PI,
    positiveCurvatureBudget: positiveCurvature * cellArea / TWO_PI,
    negativeCurvatureBudget: negativeCurvature * cellArea / TWO_PI,
    metricAreaBudget: metricAreaDensity * cellArea / Math.PI
  };
}

/**
 * Bounded refinement with grid-origin sensitivity checks and empirical
 * Richardson error estimates. The estimates are diagnostics, not rigorous
 * error bounds: gap openness alone does not prove asymptotic error scaling or
 * bound the unknown global Hessian from two sampled grids.
 */
function qiWuZhangGlobalGeometry(m, gridSize = 80, maxRefinements = 3) {
  if (!Number.isFinite(m)) throw new TypeError('Mass parameter m must be finite.');
  if (Math.abs(m + 2) < EPS || Math.abs(m) < EPS || Math.abs(m - 2) < EPS) {
    throw new RangeError('Band gap closes at a topological phase boundary for m=' + m + '.');}
  if (!Number.isInteger(gridSize) || gridSize < 4) throw new RangeError('gridSize must be an integer >= 4.');
  if (!Number.isInteger(maxRefinements) || maxRefinements < 1 || maxRefinements > 5) {
    throw new RangeError('maxRefinements must be an integer between 1 and 5.');
  }

  const gapDistance = Math.min(Math.abs(m + 2), Math.abs(m), Math.abs(m - 2));
  const gapAwareToleranceScale = Math.min(1, Math.max(0.05, gapDistance / 0.25));
  const rawChernNumber = qiWuZhangChernNumber(m, gridSize);
  const chernNumber = Math.round(rawChernNumber);
  const chernIntegerResidual = Math.abs(rawChernNumber - chernNumber);
  const initial = qiWuZhangLocalIntegrals(m, gridSize, 0.5);

  let currentGridSize = gridSize;
  let currentMidpoint = initial;
  let currentVertex = qiWuZhangLocalIntegrals(m, currentGridSize, 0);
  let curvatureQuadratureError = Infinity;
  let metricAreaQuadratureError = Infinity;
  let gridAlignmentCurvatureDiscrepancy = Math.abs(currentVertex.integratedCurvature - currentMidpoint.integratedCurvature);
  let gridAlignmentAreaDiscrepancy = Math.abs(currentVertex.metricAreaBudget - currentMidpoint.metricAreaBudget);
  let quadratureTolerance = 1e-3 * Math.max(1, Math.abs(currentMidpoint.metricAreaBudget));
  let quadratureConverged = false;
  let curvatureRichardsonErrorEstimate = Infinity;
  let metricAreaRichardsonErrorEstimate = Infinity;
  let previousCurvatureQuadratureError = Infinity;
  let previousMetricAreaQuadratureError = Infinity;
  let curvatureObservedOrder = null;
  let metricAreaObservedOrder = null;
  let richardsonAsymptotic = false;
  let refinementCount = 0;

  for (let level = 0; level < maxRefinements; level++) {
    const nextGridSize = currentGridSize * 2;
    const nextMidpoint = qiWuZhangLocalIntegrals(m, nextGridSize, 0.5);
    const nextVertex = qiWuZhangLocalIntegrals(m, nextGridSize, 0);
    curvatureQuadratureError = Math.abs(nextMidpoint.integratedCurvature - currentMidpoint.integratedCurvature);
    metricAreaQuadratureError = Math.abs(nextMidpoint.metricAreaBudget - currentMidpoint.metricAreaBudget);
    curvatureRichardsonErrorEstimate = curvatureQuadratureError / 3;
    metricAreaRichardsonErrorEstimate = metricAreaQuadratureError / 3;
    curvatureObservedOrder = Number.isFinite(previousCurvatureQuadratureError) && curvatureQuadratureError > 0
      ? Math.log2(previousCurvatureQuadratureError / curvatureQuadratureError) : null;
    metricAreaObservedOrder = Number.isFinite(previousMetricAreaQuadratureError) && metricAreaQuadratureError > 0
      ? Math.log2(previousMetricAreaQuadratureError / metricAreaQuadratureError) : null;
    richardsonAsymptotic = curvatureObservedOrder !== null && metricAreaObservedOrder !== null &&
      curvatureObservedOrder >= 1.5 && curvatureObservedOrder <= 2.5 &&
      metricAreaObservedOrder >= 1.5 && metricAreaObservedOrder <= 2.5;
    gridAlignmentCurvatureDiscrepancy = Math.abs(nextVertex.integratedCurvature - nextMidpoint.integratedCurvature);
    gridAlignmentAreaDiscrepancy = Math.abs(nextVertex.metricAreaBudget - nextMidpoint.metricAreaBudget);
    quadratureTolerance = 1e-3 * Math.max(1, Math.abs(nextMidpoint.metricAreaBudget)) * gapAwareToleranceScale;
    currentGridSize = nextGridSize;
    currentMidpoint = nextMidpoint;
    refinementCount++;
    previousCurvatureQuadratureError = curvatureQuadratureError;
    previousMetricAreaQuadratureError = metricAreaQuadratureError;
    quadratureConverged =
      curvatureQuadratureError <= quadratureTolerance &&
      metricAreaQuadratureError <= quadratureTolerance &&
      gridAlignmentCurvatureDiscrepancy <= quadratureTolerance &&
      gridAlignmentAreaDiscrepancy <= quadratureTolerance;
    if (quadratureConverged) break;
  }

  // Empirical Richardson estimate /3 with a safety multiplier. This is not a
  // theorem-backed upper bound; acceptance also requires direct refinement
  // and grid-origin convergence below.
  const curvatureQuadratureSafetyEstimate = 2 * curvatureRichardsonErrorEstimate;
  const metricAreaQuadratureSafetyEstimate = 2 * metricAreaRichardsonErrorEstimate;
  const quadratureEstimatesFinite = Number.isFinite(curvatureQuadratureSafetyEstimate) &&
    Number.isFinite(metricAreaQuadratureSafetyEstimate);

  const topologicalFloor = Math.abs(chernNumber);
  const metricAreaExcess = currentMidpoint.metricAreaBudget - topologicalFloor;
  const topologicalSaturationRaw = currentMidpoint.metricAreaBudget > EPS
    ? topologicalFloor / currentMidpoint.metricAreaBudget : 0;
  const topologicalSaturation = Math.max(0, Math.min(1, topologicalSaturationRaw));
  const hTopological = (1 + topologicalSaturation) / 2;
  const STopological = heat(hTopological);
  const psiTopological = CONE + STopological;
  const p = currentMidpoint.positiveCurvatureBudget;
  const n = currentMidpoint.negativeCurvatureBudget;
  const area = currentMidpoint.metricAreaBudget;
  const signedTopologicalPolarization = Math.sign(chernNumber) * topologicalSaturation;
  const topologicalPositiveOrientationProbability = (1 + signedTopologicalPolarization) / 2;
  const curvatureOrientationEntropyNats = binaryEntropyNats(topologicalPositiveOrientationProbability);
  const curvatureOrientationEntropyBits = curvatureOrientationEntropyNats / Math.LN2;
  const curvatureBudgetTotal = p + n;
  const curvatureBudgetPositiveProbability = curvatureBudgetTotal > EPS ? p / curvatureBudgetTotal : null;
  const curvatureBudgetEntropyNats = curvatureBudgetPositiveProbability === null
    ? null : binaryEntropyNats(curvatureBudgetPositiveProbability);
  const curvatureOrientationEntropyResidual = curvatureBudgetEntropyNats === null
    ? Infinity : Math.abs(curvatureOrientationEntropyNats - curvatureBudgetEntropyNats);
  const curvatureMixingIndex = area > EPS ? (p * n) / (area * area) : 0;
  const curvatureMixingResidual = Math.abs(STopological - curvatureMixingIndex);
  const curvatureChernResidual = Math.abs(currentMidpoint.integratedCurvature - chernNumber);
  const minorityCurvatureBudget = Math.min(p, n);
  const curvatureCancellationIdentityResidual = Math.abs(metricAreaExcess - 2 * minorityCurvatureBudget);
  const curvatureOrientationVariance = 4 * STopological;
  const curvatureOrientationVarianceFromBudgets = 4 * curvatureMixingIndex;
  const curvatureOrientationVarianceResidual = Math.abs(curvatureOrientationVariance - curvatureOrientationVarianceFromBudgets);

  // A finite empirical estimate is insufficient if bounded refinement has not
  // converged under both consecutive-grid and grid-origin checks.
  const topologicalMappingValid = quadratureConverged && quadratureEstimatesFinite &&
    curvatureQuadratureSafetyEstimate <= quadratureTolerance &&
    metricAreaQuadratureSafetyEstimate <= quadratureTolerance &&
    chernIntegerResidual <= 1e-6 &&
    curvatureChernResidual <= quadratureTolerance &&
    curvatureCancellationIdentityResidual <= 2 * quadratureTolerance &&
    Number.isFinite(curvatureOrientationEntropyResidual) &&
    curvatureOrientationEntropyResidual <= 2 * quadratureTolerance &&
    metricAreaExcess >= -quadratureTolerance;

  return {
    chernNumber, rawChernNumber, chernIntegerResidual,
    integratedCurvature: currentMidpoint.integratedCurvature,
    absoluteCurvatureBudget: currentMidpoint.absoluteCurvatureBudget,
    positiveCurvatureBudget: currentMidpoint.positiveCurvatureBudget,
    negativeCurvatureBudget: currentMidpoint.negativeCurvatureBudget,
    curvatureCancellationBudget: Math.max(0, currentMidpoint.absoluteCurvatureBudget - Math.abs(currentMidpoint.integratedCurvature)),
    metricAreaBudget: currentMidpoint.metricAreaBudget,
    topologicalFloor, metricAreaExcess,
    topologicalSaturationRaw, topologicalSaturation, signedTopologicalPolarization,
    curvatureOrientationEntropyNats, curvatureOrientationEntropyBits,
    curvatureBudgetEntropyNats, curvatureOrientationEntropyResidual,
    hTopological, STopological, psiTopological,
    curvatureMixingIndex, curvatureMixingResidual,
    minorityCurvatureBudget, curvatureChernResidual, curvatureCancellationIdentityResidual,
    curvatureOrientationVariance, curvatureOrientationVarianceFromBudgets, curvatureOrientationVarianceResidual,
    acceptedPsiTopological: topologicalMappingValid ? psiTopological : null,
    topologicalMappingValid,
    // Empirical Richardson safety estimates; not certified error bounds.
    curvatureQuadratureSafetyEstimate, metricAreaQuadratureSafetyEstimate,
    quadratureEstimatesFinite, quadratureErrorEstimateKind: 'empirical-richardson',
    // Prior diagnostics retained as non-gating telemetry.
    baseMetricAreaBudget: initial.metricAreaBudget,
    refinedIntegratedCurvature: currentMidpoint.integratedCurvature,
    refinedAbsoluteCurvatureBudget: currentMidpoint.absoluteCurvatureBudget,
    refinedMetricAreaBudget: currentMidpoint.metricAreaBudget,
    curvatureQuadratureError, metricAreaQuadratureError,
    curvatureRichardsonErrorEstimate, metricAreaRichardsonErrorEstimate,
    curvatureObservedOrder, metricAreaObservedOrder, richardsonAsymptotic,
    gapDistance, gapAwareToleranceScale,
    gridAlignmentCurvatureDiscrepancy, gridAlignmentAreaDiscrepancy,
    quadratureTolerance, quadratureConverged,
    refinementCount, refinedGridSize: currentGridSize
  };
}
module.exports = { qiWuZhangLowerBandState, qiWuZhangChernNumber, qiWuZhangLocalQGT, qiWuZhangGlobalGeometry };
