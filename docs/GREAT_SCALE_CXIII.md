# Great Scale CXIII — Empirical Failure Dependence

## Research question
CXII counts declared fault domains, but domain labels are not evidence that failure modes are independent. CXIII adds a descriptive analyzer for controlled trial records, where each observer has a boolean failure outcome.

## Pairwise statistics
For binary failure indicators A and B:
- pA = observed failure rate for A;
- pB = observed failure rate for B;
- pAB = observed joint-failure rate;
- independence benchmark = pA pB;
- excess joint failure = pAB - pA pB.

The phi correlation is (pAB - pA pB) / sqrt(pA(1-pA)pB(1-pB)), when the denominator is nonzero. Positive excess is consistent with co-failure dependence in the sample. It is not by itself a causal finding.

## Domain comparison
The module summarizes pairwise excess joint-failure values for observer pairs sharing a declared domain and pairs with different declared domains. This is exploratory: pair observations overlap, trial counts may be small, and a difference does not establish causality or generalize automatically.

## Tests
Tests cover perfect co-failure, a balanced zero-excess pattern, constant outcomes, malformed/missing observations, empty trials, repeated observer IDs, and domain-pair summaries. Run:
`python -m unittest tests/test_cxiii_empirical_failure_dependence.py`

## Scientific boundaries
No confidence intervals, hypothesis tests, causal identification, or independence certification are provided. Use predeclared trial protocols, representative failure injection, and uncertainty analysis before operational conclusions. Missing trials and selective reporting can bias results.

## Great Scale mapping
CXII: count declared domains.
CXIII: compare declared domains with observed co-failure patterns.
The next rung should add uncertainty intervals and predeclared inference procedures without confusing statistical non-detection with evidence of independence.
