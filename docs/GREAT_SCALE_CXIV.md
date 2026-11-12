# Great Scale CXIV — Uncertainty-Aware Failure Dependence

## Question
CXIII measured observed co-failure beyond an independence benchmark. CXIV asks how uncertain that estimate is with finite paired trials.

## Mathematics
For paired binary outcomes A_i,B_i in {0,1}:

\[
\hat p_A=\frac1n\sum_i A_i,\quad
\hat p_B=\frac1n\sum_i B_i,\quad
\hat p_{AB}=\frac1n\sum_i A_iB_i.
\]

\[
\hat\Delta=\hat p_{AB}-\hat p_A\hat p_B.
\]

Positive excess means more joint failures than the product-of-marginals benchmark in this sample; negative excess means fewer. This is association, not a causal explanation.

## Method and decision labels
Resample whole (A_i,B_i) rows with replacement, recompute excess, and report a two-sided percentile bootstrap interval at nominal level 1-alpha. Keeping rows paired is essential; independently resampling A and B would erase the observed pairing. Seed and replicate count make the computation reproducible.

- INSUFFICIENT_DATA: fewer than the predeclared min_trials.
- EVIDENCE_OF_POSITIVE_EXCESS: interval lower endpoint > 0.
- EVIDENCE_OF_NEGATIVE_EXCESS: interval upper endpoint < 0.
- INCONCLUSIVE: otherwise.

These are operational labels, not proofs. INCONCLUSIVE does not establish independence. The default minimum of 20 is a workflow gate, not a universally justified sample-size threshold; choose it prospectively.

## Great Scale mapping
Observed excess → interval of plausible sampling variation → bounded decision label.

Unlike deterministic error envelopes from earlier rungs, this interval depends on a sampling model. Naive row bootstrap assumes trial rows are sufficiently exchangeable/independent. Clustering, time dependence, rare failures, adaptive collection, and repeated comparisons require suitable cluster/block methods or multiplicity-aware inference.

## Synthetic example
For 20 synthetic paired trials: 10 (1,1) rows and 10 (0,0) rows. Then p_A=p_B=p_AB=0.5 and excess = 0.5 - 0.25 = 0.25. This is not production data.

## Limits / next rung
The interval does not identify every common cause, validate declared fault domains, or make correlated trials independent. CXV should handle cluster-aware uncertainty by resampling independent fault domains/deployment units and sensitivity-testing plausible intra-cluster correlation.
