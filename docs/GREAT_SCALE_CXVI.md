# Great Scale CXVI — Cluster-Size and Dependence Sensitivity

## Question
How sensitive is a paired binary failure-dependence conclusion to row independence, cluster resampling, unequal cluster sizes, and assumed within-cluster correlation?

## Statistic
For paired outcomes, excess joint failure is
\[
\Delta = \hat p_{AB} - \hat p_A\hat p_B.
\]
CXVI compares CXIV's row-resampled interval with CXV's cluster-resampled interval for the same data. Both existing point estimates are pooled/trial-weighted.

## Unequal cluster-size sensitivity
Let \(n\) be total trials, \(K\) clusters, \(\bar m=n/K\) mean cluster size, and \(CV_m\) the coefficient of variation of cluster size. For user-supplied hypothetical intracluster correlation \(\rho\):
\[
DEFF \approx 1 + \left[(1+CV_m^2)\bar m - 1\right]\rho,
\qquad n_{eff}\approx n/DEFF.
\]
This is a sensitivity heuristic, not an estimated ICC or a confidence interval. It is rough for few clusters, informative unequal cluster sizes, complex dependence, or rare binary events. The scenarios do not prove any particular ICC is true.

## Great Scale interpretation
- More raw trials do not guarantee more independent information.
- A row-bootstrap/cluster-bootstrap interval-width or status change warns that the conclusion depends on sampling assumptions.
- An ICC grid shows how nominal sample size may shrink under hypothetical dependence.
- Neither an interval spanning zero nor a narrow interval proves independence.

## Validation
Tests cover unequal cluster sizes, decreasing effective sample size as assumed ICC increases, invalid ICC rejection, empty input, and reproducibility. Tests are authored; do not describe them as executed unless the repository test runner confirms it.
