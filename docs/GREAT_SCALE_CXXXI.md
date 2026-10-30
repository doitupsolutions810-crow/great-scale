# Great Scale CXXXI — Sharp Support Bounds vs Auxiliary Margins

## Question
Can auxiliary sample extrema tighten the bounds without sacrificing guaranteed containment of the finite-population mean?

## Mathematical result
Suppose the finite population has G units, n observed values x_i, m=G-n missing values, and every value is known to lie in [L,U]. Let S be the sum of observed values. Then
\[
\boxed{\frac{S+mL}{G}\leq \mu_G\leq\frac{S+mU}{G}}.
\]
These bounds are sharp: setting every missing value to L attains the lower endpoint, and setting every missing value to U attains the upper endpoint. No narrower interval is guaranteed from the observed values and support alone.

An auxiliary sample's minimum and maximum are not population support limits. Replacing [L,U] with expanded auxiliary extrema can narrow the interval, but does not preserve the guarantee unless an additional assumption justifies those limits.

## Experiment
The script compares margin d=0.05 intervals with sharp [0,1] support bounds over 5,000 repetitions, with 120 observed units and 12 auxiliary units, across original, heldout-spiky, and heldout-skewed synthetic populations. The known-support interval is guaranteed to contain the finite-population mean by construction when the support assumption is true. The auxiliary method is evaluated empirically only.

## Interpretation
The support bounds can be wide, but their guarantee is assumption-grounded rather than calibration-grounded. Auxiliary bounds may be more informative, but their validity requires a defensible structural restriction (for example, externally established subgroup limits), not merely observed extrema.

## Great Scale map
CXXIX: calibration changes across populations.
CXXX: a frozen margin can fail on a held-out spiky population.
CXXXI: sharp support bounds identify what is guaranteed under minimal support assumptions, exposing the precision-versus-assumption trade-off.
Next: derive sharper bounds using predeclared, independently justified stratum-specific supports, and prove that they remain sharp under those assumptions.
