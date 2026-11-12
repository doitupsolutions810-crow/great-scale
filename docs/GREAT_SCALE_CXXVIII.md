# Great Scale CXXVIII — The Margin–Coverage Frontier

## Question
How does a prespecified expansion margin change empirical containment and interval width, and can a margin be selected from one scenario and claimed to guarantee coverage elsewhere?

## Experimental design
The finite synthetic population contains 240 outcomes: 216 zeros, 18 values of 0.25, and 6 values of 1. Its exact mean is 0.04375. In each of 5,000 repetitions (seed 20261010), 120 units are observed and 12 distinct units are used as the auxiliary sample. Remaining units are treated as missing for the bound calculation. Candidate limits are the auxiliary minimum and maximum expanded by margin d and clipped to [0,1].

For observed sum S, G population units, m missing units, and candidate limits [L,U]:
\[
I(d)=\left[\frac{S+mL(d)}{G},\frac{S+mU(d)}{G}\right],
\quad W(d)=\frac{m}{G}(U(d)-L(d)).
\]

## Results
| Margin d | Empirical containment | Mean interval width |
|---:|---:|---:|
| 0 | 73.76% | 0.193525 |
| 0.025 | 76.02% | 0.202648 |
| 0.05 | 94.54% | 0.211770 |
| 0.1 | 100.00% | 0.230015 |
| 0.2 | 100.00% | 0.266505 |
| 0.5 | 100.00% | 0.375975 |
| 1.0 | 100.00% | 0.500000 |

These figures are reproduced by the companion script's fixed seed. They describe only this synthetic finite population and this sampling design. A 100% observed containment rate does not prove a universal guarantee. At d=1, clipping yields the known support [0,1], which is valid here by construction.

## Finding
There is a measurable coverage–width frontier: expanding the margin increased containment in this experiment, at the cost of wider intervals. The d=0.05 setting achieved 94.54% empirical containment, but this is not a calibrated 95% confidence guarantee. Selecting d to hit a target on the same experiment would be tuning, not proof. General claims require independent validation and a theoretical justification under explicit assumptions.

## Great Scale mapping
CXXVI: sample extrema can fail as support limits.
CXXVII: repeated sampling measures the failure.
CXXVIII: margin size traces the empirical coverage–width frontier.
Next: evaluate transfer to shifted populations and choose calibration on a separate calibration set, reporting held-out performance separately.
