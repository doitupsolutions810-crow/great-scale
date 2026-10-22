(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.GreatScaleRisk = api;
})(typeof globalThis === 'undefined' ? this : globalThis, function () {
  const MAX_GROUPS = 10000;

  function computeRiskCertificate({ successes, trialsPerGroup, supportGap, confidence = 0.95, scale = 1 } = {}) {
    if (!Array.isArray(successes) || successes.length === 0) {
      throw new TypeError('successes must be a non-empty array');
    }
    if (successes.length > MAX_GROUPS) {
      throw new RangeError(`successes must contain at most ${MAX_GROUPS} groups`);
    }
    if (!Number.isSafeInteger(trialsPerGroup) || trialsPerGroup < 1) {
      throw new RangeError('trialsPerGroup must be a positive integer');
    }
    if (!Number.isFinite(supportGap) || supportGap <= 0 || supportGap >= 1) {
      throw new RangeError('supportGap must be between 0 and 1');
    }
    if (!Number.isFinite(confidence) || confidence <= 0 || confidence >= 1) {
      throw new RangeError('confidence must be between 0 and 1');
    }
    if (!Number.isFinite(scale) || scale <= 0) {
      throw new RangeError('scale must be positive and finite');
    }
    for (const count of successes) {
      if (!Number.isSafeInteger(count) || count < 0 || count > trialsPerGroup) {
        throw new RangeError('each success count must be an integer within the trial count');
      }
    }

    const groupCount = successes.length;
    const alpha = 1 - confidence;
    const supportMaximum = 1 - supportGap;
    if (supportMaximum >= 1) {
      throw new RangeError('supportGap is too small to represent a support maximum below 1');
    }
    const maximumLoss = -scale * Math.log(supportGap);
    const center = successes.reduce((sum, count) => {
      const observedRate = Math.min(supportMaximum, count / trialsPerGroup);
      return sum - scale * Math.log1p(-observedRate);
    }, 0) / groupCount;
    const measurementRadius = (scale / supportGap)
      * Math.sqrt(Math.log((4 * groupCount) / alpha) / (2 * trialsPerGroup));
    const samplingRadius = maximumLoss
      * Math.sqrt(Math.log(4 / alpha) / (2 * groupCount));
    const radius = measurementRadius + samplingRadius;
    if (![maximumLoss, center, measurementRadius, samplingRadius, radius].every(Number.isFinite)) {
      throw new RangeError('risk certificate exceeds the finite numeric range');
    }

    return {
      groupCount,
      trialsPerGroup,
      supportGap,
      supportMaximum,
      confidence,
      center,
      measurementRadius,
      samplingRadius,
      radius,
      lowerBound: Math.max(0, center - radius),
      upperBound: Math.min(maximumLoss, center + radius),
      maximumLoss,
    };
  }

  function classifyRisk(certificate, riskLimit) {
    if (!certificate || !Number.isFinite(certificate.lowerBound)
      || !Number.isFinite(certificate.upperBound)
      || certificate.lowerBound < 0
      || certificate.upperBound < certificate.lowerBound) {
      throw new TypeError('certificate must contain valid lowerBound and upperBound values');
    }
    if (!Number.isFinite(riskLimit) || riskLimit < 0) {
      throw new RangeError('riskLimit must be non-negative and finite');
    }
    if (certificate.upperBound <= riskLimit) return 'within-limit';
    if (certificate.lowerBound > riskLimit) return 'above-limit';
    return 'indeterminate';
  }

  function secondMomentCoefficient(supportMaximum) {
    if (supportMaximum >= 1e-3) {
      return (-Math.log1p(-supportMaximum) - supportMaximum)
        / (supportMaximum * supportMaximum);
    }

    let partial = 0;
    let power = 1;
    const lastOrder = 20;
    for (let order = 2; order <= lastOrder; order++) {
      partial += power / order;
      power *= supportMaximum;
    }
    const tailUpperBound = power / ((lastOrder + 1) * (1 - supportMaximum));
    return partial + tailUpperBound;
  }

  function pointLoss(probability, scale) {
    return -scale * Math.log1p(-probability);
  }

  function sharpMomentExtremizers(mean, variance, supportMaximum, scale) {
    if (variance === 0) {
      const pointMass = [{ value: mean, probability: 1 }];
      const loss = pointLoss(mean, scale);
      return {
        lowerBound: loss,
        upperBound: loss,
        lowerExtremizer: pointMass,
        upperExtremizer: pointMass,
        boundaryMass: 0,
      };
    }

    const lowerUpperAtom = mean + variance / mean;
    const lowerUpperWeight = mean / lowerUpperAtom;
    const lowerExtremizer = [
      { value: 0, probability: 1 - lowerUpperWeight },
      { value: lowerUpperAtom, probability: lowerUpperWeight },
    ];
    const lowerBound = lowerUpperWeight * pointLoss(lowerUpperAtom, scale);

    const distanceToBoundary = supportMaximum - mean;
    const upperLowerAtom = mean - variance / distanceToBoundary;
    const upperBoundaryWeight = variance
      / (distanceToBoundary * distanceToBoundary + variance);
    const upperExtremizer = [
      { value: upperLowerAtom, probability: 1 - upperBoundaryWeight },
      { value: supportMaximum, probability: upperBoundaryWeight },
    ];
    const upperBound = (1 - upperBoundaryWeight) * pointLoss(upperLowerAtom, scale)
      + upperBoundaryWeight * -scale * Math.log1p(-supportMaximum);

    return {
      lowerBound,
      upperBound,
      lowerExtremizer,
      upperExtremizer,
      boundaryMass: upperBoundaryWeight,
    };
  }

  function computeMomentLogLossBound({ mean, variance, supportGap, scale = 1 } = {}) {
    if (!Number.isFinite(supportGap) || supportGap <= 0 || supportGap >= 1) {
      throw new RangeError('supportGap must be between 0 and 1');
    }
    if (!Number.isFinite(scale) || scale <= 0) {
      throw new RangeError('scale must be positive and finite');
    }

    const supportMaximum = 1 - supportGap;
    if (supportMaximum >= 1) {
      throw new RangeError('supportGap is too small to represent a support maximum below 1');
    }
    if (!Number.isFinite(mean) || mean < 0 || mean > supportMaximum) {
      throw new RangeError('mean must lie within the declared support');
    }
    const maximumVariance = mean * (supportMaximum - mean);
    if (!Number.isFinite(variance) || variance < 0 || variance > maximumVariance) {
      throw new RangeError('variance is infeasible for the declared mean and support');
    }

    const jensenLowerBound = -scale * Math.log1p(-mean);
    const chordUpperBound = scale * mean / supportMaximum * -Math.log(supportGap);
    const curvatureUpperBound = jensenLowerBound
      + scale * variance / (2 * supportGap * supportGap);
    const seriesFactor = secondMomentCoefficient(supportMaximum);
    const secondMomentUpperBound = scale * (
      mean + (mean * mean + variance) * seriesFactor
    );
    const sharp = sharpMomentExtremizers(mean, variance, supportMaximum, scale);
    const asymptoticBoundaryMass = variance
      / (variance + (1 - mean) * (1 - mean));
    const asymptoticLogLossCoefficient = scale * asymptoticBoundaryMass;
    if (![jensenLowerBound, chordUpperBound, curvatureUpperBound, secondMomentUpperBound,
      sharp.lowerBound, sharp.upperBound, asymptoticLogLossCoefficient].every(Number.isFinite)) {
      throw new RangeError('moment certificate exceeds the finite numeric range');
    }

    return {
      mean,
      variance,
      supportGap,
      supportMaximum,
      scale,
      lowerBound: sharp.lowerBound,
      upperBound: sharp.upperBound,
      sharpLowerBound: sharp.lowerBound,
      sharpUpperBound: sharp.upperBound,
      lowerExtremizer: sharp.lowerExtremizer,
      upperExtremizer: sharp.upperExtremizer,
      boundaryMass: sharp.boundaryMass,
      asymptoticBoundaryMass,
      asymptoticLogLossCoefficient,
      jensenLowerBound,
      chordUpperBound,
      curvatureUpperBound,
      secondMomentUpperBound,
      secondMomentCoefficient: seriesFactor,
      boundType: 'sharp-moment-extremal',
      decisionScope: 'conditional-model-only',
      greatScaleStatus: 'conditional research sidecar; no canonical level assigned',
      evidenceVerified: false,
      evidenceStatus: 'deterministic bound conditional on exact moments and declared support',
    };
  }

  return { computeRiskCertificate, computeMomentLogLossBound, classifyRisk };
});
