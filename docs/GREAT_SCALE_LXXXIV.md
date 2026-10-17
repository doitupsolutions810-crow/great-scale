# Great Scale LXXXIV — Evidence Independence and Common-Cause Failure

## Pinned finding
Multiple observations strengthen a conclusion only to the extent that their error mechanisms provide genuinely additional information. Different files, providers, instruments, or analysts do not by themselves establish independence. Shared calibration, source data, model assumptions, operators, infrastructure, or selection procedures can create common-cause failure.

## Probability model
For hypothesis H and evidence streams E1 and E2, conditional independence under H requires P(E1,E2 | H) = P(E1 | H) P(E2 | H). For Bayesian evidence-ratio multiplication, the corresponding factorization must also be justified under not-H.

With a shared latent cause Z: P(E1,E2 | H) = sum_z P(z | H) P(E1 | H,z) P(E2 | H,z), which generally does not factor into marginal probabilities.

## Correlated-error floor
For n equal-variance observations with variance sigma^2 and exchangeable pairwise error correlation rho:

Var(mean) = sigma^2 [1 + (n-1)rho] / n = sigma^2 [rho + (1-rho)/n].

For rho > 0, the limit as n tends to infinity is rho sigma^2. Repetition reduces unshared noise but cannot remove common-mode variance. This is a stochastic correlation floor, distinct from LXXXI's deterministic bias bound.

The exchangeable-model effective sample size is n_eff = n / [1 + (n-1)rho]. Example: n=10, rho=0.2 gives n_eff approximately 3.57 and Var(mean)=0.28 sigma^2.

## Validation and limits
Unit tests can check arithmetic and conservative provenance interpretation, but cannot prove real-world independence or identify undeclared causes. Scientific use requires a causal dependency inventory, calibration lineage, source-data/model provenance, and—where feasible—controlled fault injection or replication using independently generated data and failure mechanisms.

## Great Scale transition
- LXXXI: repetition encounters a persistent bias floor.
- LXXXII: calibration assumptions can become invalid.
- LXXXIII: invalid upstream certificates revoke dependent conclusions.
- LXXXIV: apparently separate evidence paths may share an unrecorded upstream cause.

Next: diversity of failure mechanisms—designing evidence collection so independence is supported by architecture and tested rather than merely asserted.
