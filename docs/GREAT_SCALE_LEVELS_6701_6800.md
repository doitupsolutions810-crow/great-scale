# Great Scale — Levels 6701–6800: separate extremal certainty from empirical uncertainty

## Finding

The risk-certificate work in the repository exposes a subtle but consequential distinction:

**A mathematically sharp bound conditional on exact inputs is not automatically a statistically valid bound for estimated inputs.**

For the loss \(f(P)=-a\ln(1-P)\), the two-moment extremal calculation can produce the exact minimum and maximum of \(\mathbb E[f(P)]\) over distributions having specified exact mean \(p\), variance \(v\), and justified support \(0\le P\le b=1-\delta<1\). That is a theorem about a constrained family of distributions.

In an actual data pipeline, \(p\) and \(v\) are commonly estimated, and the support gap \(\delta\) may be an assumption rather than an observed or independently justified fact. Plugging point estimates into a sharp exact-moment formula does not propagate sampling uncertainty, dependence, selection bias, or support uncertainty. Calling the resulting interval a confidence interval would therefore overstate what was proved.

This is a stronger finding than “the formula is sharp”: **sharpness, statistical coverage, and validity of the support assumption are three separate proof obligations.**

## Mathematics: three nested sets

Let \(\mathcal D(p,v,b)\) be the set of all probability distributions on \([0,b]\) with exact moments \(\mathbb E[P]=p\) and \(\operatorname{Var}(P)=v\). For \(f(P)=-a\ln(1-P)\), with \(a>0\) and \(b<1\), define the conditional extremal interval

\[
L(p,v,b)=\inf_{D\in\mathcal D(p,v,b)}\mathbb E_D[f(P)],
\qquad
U(p,v,b)=\sup_{D\in\mathcal D(p,v,b)}\mathbb E_D[f(P)].
\]

When the moment/support constraints are feasible and the extremizers are correctly characterized, \([L,U]\) is sharp for that exact constraint set. It does not by itself cover uncertainty in the inputs.

If data produce a confidence or uncertainty set \(\mathcal C\) for the unknown parameters \((p,v,b,a)\), a conservative propagated interval must instead account for all admissible parameter values, for example

\[
L_{\mathcal C}=\inf_{(p',v',b',a')\in\mathcal C}L(p',v',b',a'),
\qquad
U_{\mathcal C}=\sup_{(p',v',b',a')\in\mathcal C}U(p',v',b',a').
\]

This outer optimization is only as defensible as the construction of \(\mathcal C\), including its coverage or robustness guarantees and any dependence assumptions. A point estimate is not a confidence set.

The support boundary is especially important. Since \(f(P)\to+\infty\) as \(P\to1^{-}\), allowing \(b=1-\delta\) to approach one can make the sharp upper endpoint diverge while exact interior moments remain fixed in the nondegenerate cases described by the risk-certificate note. Therefore a chosen \(\delta>0\) must be justified independently; it cannot be inferred merely because the formula requires \(b<1\).

## Great Scale mapping

| Level | Mathematics | Engineering interpretation | Required gate |
|---|---|---|---|
| 6701 | Exact-moment extremum is conditional on \((p,v,b,a)\) | Label the assumptions that define the admissible distribution family | Input provenance and feasibility |
| 6710 | \([L,U]\) is sharp over \(\mathcal D(p,v,b)\), not over unknown parameter values | Do not label a sharp extremal range as a confidence interval | Explicit interval semantics |
| 6720 | Outer infimum/supremum over \(\mathcal C\) propagates parameter uncertainty | Add a separate estimator/uncertainty layer | Coverage or robust-set contract |
| 6730 | \(f(P)\) is unbounded as \(P\to1^{-}\) | The support gap \(\delta\) controls whether finite upper-risk claims are possible | Independently justified support bound |
| 6740 | Repeated observations do not automatically imply independent groups | Cluster dependence and selection mechanisms change uncertainty calculations | Sampling-design contract |
| 6800 | A defensible result requires model, support, and statistical assumptions to be separately visible | Do not compress mathematical sharpness into one undifferentiated “confidence” score | All assumption gates pass |

## Falsifiable test plan

1. **Exact-moment oracle:** for feasible small finite-support distributions, verify that every reported extremal witness reproduces the supplied mean and variance and that its expected loss matches the reported endpoint within the stated numerical tolerance.
2. **Input-feasibility tests:** reject impossible moment/support combinations before calculating a certificate; explicitly test degenerate boundaries such as \(p=0\), \(p=b\), and \(v=0\).
3. **Uncertainty-layer test:** construct a nontrivial parameter set \(\mathcal C\) containing multiple feasible \((p,v,b)\) values; verify the propagated interval encloses the conditional interval for every member of \(\mathcal C\).
4. **Support sensitivity:** decrease \(\delta\) across a controlled sequence while holding admissible interior moments fixed; verify that the implementation does not claim a uniform finite upper bound when the analytic upper endpoint grows without bound.
5. **Dependence test:** simulate clustered data under within-group dependence and verify that an estimator's stated uncertainty procedure does not silently use an independent-observation formula.
6. **Semantics test:** API and UI labels must distinguish “sharp conditional extremal range”, “sampling confidence interval”, and “robust uncertainty interval”; these labels are not interchangeable.
7. **Reproducibility:** store the moment estimates, support justification, sampling design, estimator version, assumptions, and exact code revision alongside the certificate.

## Repository integration boundary

- The risk/descent certificate branch documents the exact-moment, bounded-support result and the divergence as \(\delta\to0\).
- The proof-kernel/promotion branch addresses structural proof validation and execution evidence. It should not claim to certify statistical coverage merely because a JSON certificate passes structural validation.
- A future integration should pass a typed certificate containing (1) conditional extremal result, (2) parameter uncertainty contract, (3) support-bound provenance, and (4) sampling/dependence assumptions. The verifier should preserve these as distinct fields rather than infer missing assumptions.
- This note does not claim that the risk sidecar is wired into the live state engine or that the outer uncertainty optimization is implemented.

## Verification status

- **Mathematics:** the distinction between optimization over a fixed feasible distribution set and uncertainty over estimated parameters follows directly from the definitions of the two optimization problems.
- **Repository basis:** the current risk-certificate documentation explicitly says the sharp interval assumes exact moments and justified support, and that estimated moments require their own uncertainty treatment.
- **Tests:** this document specifies falsifiable tests; it does not claim they were executed by this review.
- **Science:** no empirical quantum claim is made. Any physical interpretation requires validated measurements, a justified observation model, uncertainty quantification, and reproducible data.
- **Promotion:** keep this level research-only until the estimator/uncertainty layer and its test evidence exist.

## Conclusion

The Great Scale should expose at least three independent statuses for this class of result:

- extremal_status: whether the conditional optimization is valid for the supplied exact constraints;
- support_status: whether the support bound is independently justified;
- statistical_status: whether uncertainty in estimated inputs and dependence has been handled with stated guarantees.

A result is not fully evidence-ready merely because its conditional extremum is mathematically sharp.
