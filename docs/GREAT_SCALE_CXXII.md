# Great Scale CXXII — Partial Identification Under Unknown Selection

## Question
If selection probabilities are unknown but plausibly bounded, what range of weighted estimates remains possible?

## Object
For observed cluster contrasts \(\Delta_g\ge0\), and inclusion probabilities \(\pi_g\in[\underline\pi,\overline\pi]\), consider
\[
\mu_H(\boldsymbol\pi)=
\frac{\sum_{g:S_g=1}\Delta_g/\pi_g}
{\sum_{g:S_g=1}1/\pi_g}.
\]
Since weights lie in \([1/\overline\pi,1/\underline\pi]\), the smallest weighted mean assigns the smallest weight to positive contrasts and largest weights to zeros; the largest does the reverse. The implementation calculates these extrema for nonnegative contrasts.

## Interpretation
The output is a sensitivity interval for the selected-sample weighted mean under the specified probability range. It is **not** a confidence interval and does not, by itself, bound the full-population target when the unobserved clusters' outcomes are unknown. A full-population partial-identification claim requires additional assumptions about missing outcomes, selection, or a known finite-population frame.

## Test
```bash
python -m unittest tests.test_cxxii_partial_identification_selection
python cxxii_partial_identification_selection.py
```
Tests check interval ordering, collapse when the probability range is a point, validation, and deterministic output. Run in a Python environment with the CXX module available before marking verified.

## Limits
Synthetic only. Bounds depend on externally justified probability limits. Signed contrasts require a general optimization routine; this implementation deliberately rejects negative values. No causal claim is implied.
