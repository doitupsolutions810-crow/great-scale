# Great Scale CXIX — Informative Cluster Size and Selection

## Research question

Can differences between cluster-weighted and trial-weighted dependence be associated with cluster size, and what can be concluded about selection into the observed dataset?

For cluster g, Δ_g = p̂_AB,g − p̂_A,g p̂_B,g. The module reports the equal-cluster mean, pooled trial-weighted contrast, and Pearson correlation between cluster size m_g and Δ_g.

## Diagnostic interpretation

- The size correlation is descriptive, not causal. Small samples, ties, nonlinear patterns, or noisy Δ estimates can obscure informative size.
- The label DIAGNOSTIC_ASSOCIATION_PRESENT is a heuristic threshold (absolute Pearson correlation at least 0.5), not a significance test.
- A low or undefined correlation does not establish non-informative cluster size.
- Observed clusters alone generally cannot identify the selection mechanism.

## Optional selection probabilities

If each observed cluster supplies a valid inclusion probability π_g, the module reports the Hájek-style estimate Σ(Δ_g/π_g) / Σ(1/π_g). This requires a defensible sampling design and assumptions about selection. The implementation can validate format and within-cluster consistency, but cannot verify that the probabilities are correct or that unmeasured selection is absent.

## Synthetic tests

Tests construct balanced clusters and perfectly paired clusters with different sizes, then verify size diagnostics, missing selection information, optional weighting, and invalid probabilities. These are software fixtures, not empirical evidence. Tests are authored but must be run in CI before merge.

## Great Scale finding

Weighting sensitivity can be diagnosed against observed cluster size, but selection bias is not identifiable from observed outcomes alone without design information or additional assumptions.

Next rung: CXIX+1 should conduct simulation-based stress tests where the true cluster population is known, then vary size–effect association and selection probabilities to measure bias and coverage.
