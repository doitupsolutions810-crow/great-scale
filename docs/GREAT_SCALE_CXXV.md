# Great Scale CXXV — Robust Bounds Under Uncertain Stratum Limits

## Question
What if subgroup outcome limits are not known exactly, but only bounded by auxiliary evidence?

## Mathematics
Suppose the lower limit in stratum h is only known to lie in [L_h^-, L_h^+], and the upper limit in [U_h^-, U_h^+]. For robust coverage across all admissible limits, use the outer endpoints:

\[
\mu_L^{rob}=\frac{1}{G}\sum_h(S_h+m_hL_h^-),\qquad
\mu_U^{rob}=\frac{1}{G}\sum_h(S_h+m_hU_h^+).
\]

The robust width is:

\[
W_{rob}=\frac{1}{G}\sum_hm_h(U_h^+-L_h^-).
\]

Relative to point-valued limits, admitting uncertainty can only widen or preserve the interval. The amount of widening is weighted by the missing counts in each stratum.

## Synthetic test
A deterministic 240-cluster population has 120 clusters in stratum A with outcomes alternating 0 and 0.25, and 120 in B alternating 0 and 0.125. Seed 20261010 samples clusters at probabilities 0.35 and 0.65, yielding 111 observed clusters. The true mean is 0.09375. With nominal limits, the interval is [0.0432292, 0.1526042] (width 0.109375). Expanding each stratum's upper limit by 0.05 gives [0.0432292, 0.1794792] (width 0.13625). Both contain the known target in this draw; uncertainty increases width by 0.026875.

## Interpretation
This is a sensitivity analysis, not a confidence interval. The outer ranges must genuinely include the unknown valid limits. If the assumed outer limits still exclude possible outcomes, robustness is illusory. Sampling uncertainty in the auxiliary data needs a separate calibration procedure.

## Great Scale finding
Precision gained from stratification is conditional on the validity of subgroup constraints. Once the constraints themselves are uncertain, honest identification widens in proportion to the missing population exposed to that uncertainty. The constraint-validation problem is part of the scientific result, not a footnote.
