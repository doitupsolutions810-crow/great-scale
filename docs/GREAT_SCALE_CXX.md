# Great Scale CXX — Selection Stress Tests and Recovery

## Purpose

CXIX identified that observed clusters may not represent the target population. CXX creates a known finite synthetic population, applies controlled cluster-selection mechanisms, and compares estimators to the exact population equal-cluster mean.

## Estimand and estimators

For each cluster, Δ_g = p̂_AB,g − p̂_A,g p̂_B,g. The finite-population truth is μ_C = K⁻¹ Σ_g Δ_g. Each simulation selects clusters with known inclusion probabilities π_g and compares:

- observed equal-cluster mean;
- Hájek inverse-probability-weighted mean using the known π_g.

Metrics include Monte Carlo bias, RMSE, empirical standard deviation, and approximate percentile-bootstrap interval coverage.

## Controlled mechanisms

- size_correlated: larger clusters have higher selection probability.
- effect_correlated: clusters with positive Δ have higher selection probability.

The harness is intentionally synthetic. Because the probabilities are known by construction, it can test whether weighting helps under these specified mechanisms. This does not imply that real-world inclusion probabilities are known or that the same assumptions hold in a real dataset.

## Important limits

- The finite population uses simple repeated binary patterns; results are not general guarantees.
- The trial-weighted contrast is not the target in this harness.
- Bootstrap coverage is a diagnostic; it is not guaranteed to equal nominal coverage.
- If selection depends on unobserved features not represented in the probabilities, inverse-probability weighting may remain biased.
- The implementation does not prove causality.

## Great Scale conclusion

The scientific test is recovery against known truth, not merely agreement between two estimators. Next work should vary cluster count, effect distribution, outcome noise, positivity (very small inclusion probabilities), and misspecified selection probabilities, then record the bias/coverage frontier.
