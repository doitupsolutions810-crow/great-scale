# Great Scale CXV — Cluster-Aware Uncertainty

## Motivation
CXIV resamples paired trial rows. That is unsuitable when several rows share a deployment, observer, machine, region, or other common failure environment. Treating correlated rows as independent can understate uncertainty.

## Estimand
For paired binary outcomes A_i,B_i, CXV retains the CXIII/CXIV statistic:

\[
\hat p_A=\frac1n\sum_i A_i,\quad
\hat p_B=\frac1n\sum_i B_i,\quad
\hat p_{AB}=\frac1n\sum_i A_iB_i,
\qquad
\hat\Delta=\hat p_{AB}-\hat p_A\hat p_B.
\]

The change is the resampling unit, not the point-estimate formula. Each row must identify a cluster_id that represents a plausible independent sampling unit. A bootstrap draw samples cluster IDs with replacement and includes all rows from each selected cluster. This preserves within-cluster and within-trial pairing.

## Decision labels
- INSUFFICIENT_CLUSTERS: number of unique clusters is below the predeclared minimum.
- EVIDENCE_OF_POSITIVE_EXCESS: cluster-bootstrap interval lower endpoint > 0.
- EVIDENCE_OF_NEGATIVE_EXCESS: interval upper endpoint < 0.
- INCONCLUSIVE: otherwise.

The default minimum is 10 clusters as a workflow gate, not a universal guarantee. Bootstrap uncertainty with very few clusters is unreliable even if each cluster contains many trials.

## Mathematics visible
The naive row bootstrap resamples n individual rows. The cluster bootstrap instead resamples G cluster units:

\[
(C_1,\ldots,C_G)^*\sim\operatorname{Resample}(C_1,\ldots,C_G),
\]

then recomputes \(\hat\Delta^*\) from all rows in the sampled clusters. Its percentile interval approximates uncertainty across the sampled cluster population, under the assumed cluster sampling design.

The implementation reports a pooled, trial-weighted statistic. If cluster sizes vary, clusters are selected with equal probability but contribute all their rows; this is not the same as an equal-cluster-weighted estimand. Informative cluster size must be examined, and a different estimand may be needed.

## Synthetic check
Twelve synthetic clusters each contain three (1,1) rows and three (0,0) rows. There are 72 trials but only 12 clusters. The pooled rates are p_A=p_B=p_AB=0.5 and excess is 0.25. A separate stress test uses 300 rows from only three clusters and must return INSUFFICIENT_CLUSTERS under the default minimum.

## Limitations
This procedure does not account for shared causes across clusters, validate the cluster labels, fix informative cluster sizes, or guarantee good coverage with few clusters. Temporal blocks, hierarchical models, wild-cluster bootstrap, or randomization-based methods may be more appropriate depending on the design. Confidence intervals containing zero do not establish independence.

## Next rung: CXVI
Assess sensitivity to cluster size and intra-cluster correlation, and compare naive-row versus cluster-aware uncertainty on the same synthetic designs before making any operational decision.
