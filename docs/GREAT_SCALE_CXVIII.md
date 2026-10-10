# Great Scale CXVIII — Heterogeneity Under Uncertainty

## Question

After cluster-size sensitivity (CXVI) and weighting sensitivity (CXVII), quantify how cluster-specific binary dependence varies and whether the equal-cluster mean is distinguishable from zero under an approximate uncertainty interval.

## Estimand

For cluster g, define Δ_g = p̂_AB,g − p̂_A,g p̂_B,g. The equal-cluster target is Δ̄_C = (1/K) Σ_g Δ_g. Every cluster receives equal weight. This is not generally the same as the trial-weighted pooled contrast.

## Uncertainty method

Resample the observed cluster-specific Δ values with replacement, taking K values per replicate. The percentile interval of bootstrap means estimates uncertainty for the equal-cluster mean under cluster-level sampling assumptions.

Statuses:
- INSUFFICIENT_CLUSTERS: fewer than min_clusters; interval omitted.
- EVIDENCE_OF_POSITIVE_MEAN_CLUSTER_EXCESS: interval lower bound strictly above zero.
- EVIDENCE_OF_NEGATIVE_MEAN_CLUSTER_EXCESS: interval upper bound strictly below zero.
- INCONCLUSIVE: interval contains zero.

## Synthetic fixture

Twelve equally sized clusters: six balanced clusters with Δ=0 and six perfectly paired two-row clusters with Δ=0.25. The equal-cluster mean is 0.125 and the range is [0, 0.25]. Since cluster sizes are equal, the pooled trial-weighted contrast is also 0.125 in this fixture. These are constructed values, not observed field evidence.

## Limits

- A positive mean does not imply all clusters are positive; report heterogeneity separately.
- Percentile cluster bootstrap is approximate and can perform poorly with few clusters, rare outcomes, or unrepresentative clusters.
- The interval is not causal evidence and does not establish universal population truth.
- The default minimum of ten clusters is a guardrail, not a theorem guaranteeing coverage.
- Inputs require paired binary outcomes and nonempty cluster IDs.

## Great Scale mapping

This rung separates dependence magnitude, between-cluster heterogeneity, weighting/target-population choice, and uncertainty around the equal-cluster average.

Next rung: investigate informative cluster size and selection—whether cluster size or inclusion probability is associated with Δ. A cluster bootstrap alone does not correct informative sampling.
