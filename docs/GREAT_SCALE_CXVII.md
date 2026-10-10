# Great Scale CXVII — Weighting Sensitivity

## Scientific question
Does dependence look different when the target is a randomly selected trial versus a randomly selected cluster?

## Estimands
For pooled observations:
\[
\Delta_{trial}=\hat p_{AB}-\hat p_A\hat p_B.
\]
For cluster \(g\), calculate \(\Delta_g=\hat p_{AB,g}-\hat p_{A,g}\hat p_{B,g}\), then average clusters equally:
\[
\Delta_{cluster}=K^{-1}\sum_{g=1}^{K}\Delta_g.
\]
The difference \(\Delta_{cluster}-\Delta_{trial}\) is a weighting/heterogeneity diagnostic. It is not automatically an estimate of bias, and neither estimand is universally preferable. Choose based on the target population and study design.

## Synthetic test design
A large cluster has balanced outcomes with zero within-cluster excess; a small cluster has concordant outcomes with excess 0.25. Equal-cluster mean excess is 0.125. Pooling gives the larger cluster greater influence, so the pooled estimate differs. This is a constructed unit test, not empirical evidence.

## Limitations
- Within-cluster rates can be unstable for small clusters.
- The arithmetic mean of cluster excesses is not identical to pooled excess.
- Different weighting answers different questions; discrepancy alone does not imply which is correct.
- No confidence interval or causal identification is supplied by this descriptive module.
