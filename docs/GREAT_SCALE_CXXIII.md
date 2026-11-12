# Great Scale CXXIII — Full-Population Bounds with Missing Clusters

## Question
Given a known finite-population frame but unobserved cluster outcomes, what can be guaranteed without assuming the missing outcomes resemble the observed ones?

## Derivation
Let the population contain \(G\) clusters, of which \(n\) are observed. Let observed contrasts be \(\Delta_1,\ldots,\Delta_n\), and suppose every unobserved contrast is known only to lie in \([L,U]\). The finite-population mean is
\[
\mu_G=\frac{1}{G}\left(\sum_{i=1}^{n}\Delta_i+
\sum_{i=n+1}^{G}\Delta_i\right).
\]
With \(m=G-n\) missing clusters, the sharp bounds under these assumptions are
\[
\boxed{\frac{\sum_{i=1}^{n}\Delta_i+mL}{G}
\leq \mu_G \leq
\frac{\sum_{i=1}^{n}\Delta_i+mU}{G}.}
\]
They are sharp because assigning every missing outcome to \(L\) attains the lower bound and assigning every missing outcome to \(U\) attains the upper bound.

## Synthetic experiment
The CXX population has \(G=200\), cluster contrasts in \([0,0.25]\), and known target \(\mu_G=0.125\). The test repeatedly samples clusters under the effect-correlated selection mechanism and verifies that the target lies within the assumption-based interval. The test does not claim that the interval is narrow or probabilistic coverage.

## Test protocol
```bash
python -m unittest tests.test_cxxiii_population_bounds_missing_clusters
python cxxiii_population_bounds_missing_clusters.py
```

Tests include exhaustive enumeration of all completions for a small frame, collapse to a point when no clusters are missing, repeated synthetic target containment, and invalid-input checks.

## Limits
These are identification bounds, not confidence intervals. They require a known population size, exact observed outcomes, and defensible bounds on every missing outcome. If the outcome range is incorrect, the guarantee fails. Sampling uncertainty in observed values would require a separate inferential layer.
