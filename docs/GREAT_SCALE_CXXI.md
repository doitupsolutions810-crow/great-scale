# Great Scale CXXI — Robustness to Misspecified Selection

## Question
Does inverse-probability weighting remain reliable when the inclusion probabilities supplied to the estimator are wrong?

## Mathematical object
For finite clusters (g=1,ldots,G), let (Delta_g) be the known synthetic cluster-level dependence contrast and let (S_g\in\{0,1\}) indicate inclusion. The target is the equal-cluster mean
\[
\mu=G^{-1}\sum_{g=1}^{G}\Delta_g.
\]
The Hájek estimator with supplied probabilities \(\widehat\pi_g\) is
\[
\widehat\mu_H=
\frac{\sum_g S_g\Delta_g/\widehat\pi_g}
{\sum_g S_g/\widehat\pi_g}.
\]
The simulation generates selection with \(\pi_g=0.8\) for positive \(\Delta_g\), and \(0.25\) otherwise. It compares unweighted estimates, weights using the true \(\pi_g\), and weights using a deliberately shifted model:
\[
\widehat\pi_g=\operatorname{expit}(\operatorname{logit}(\pi_g)+\lambda).
\]
At \(\lambda=0\), supplied probabilities equal the true design probabilities. Nonzero \(\lambda\) is a controlled misspecification stress, not a fitted model.

## Diagnostics
Across repeated finite-population samples, report mean estimate, bias, RMSE, empirical standard deviation, average selected-cluster count, and effective sample size
\[
ESS=\frac{(\sum_g w_g)^2}{\sum_g w_g^2},\qquad w_g=1/\widehat\pi_g.
\]
ESS measures weight concentration; it does not diagnose bias or prove validity.

## Scientific interpretation
Correct inclusion probabilities can remove selection distortion under the simulation's design and assumptions. Wrong probabilities generally alter the target-weighting correction and may reintroduce bias. A plausible-looking point estimate or a large ESS does not establish that selection has been corrected.

## Test protocol
Run:
```bash
python -m unittest tests.test_cxxi_selection_misspecification
python cxxi_selection_misspecification.py
```
Tests check known truth, equality of true and misspecified-weight paths when \(\lambda=0\), determinism, ESS bounds, and input validation. Tests must be executed in a Python environment with the CXX module present before marking this rung verified.

## Limits
This is a finite synthetic population with known inclusion probabilities. It is not an empirical dataset, a causal result, or proof that a real selection model is correct. Real applications should vary plausible inclusion models and disclose positivity assumptions and unmeasured selection risk.
