# Great Scale — Levels 6801–6900: support-aware feasibility before sharp certification

## Finding

The risk-certificate documentation defines its admissible random variable on the narrower support \(0\le P\le b=1-\delta<1\). The separate feasibility-certificate research describes the familiar probability-moment inequality \(v\le p(1-p)\). That inequality is correct for the generic support \([0,1]\), but it is not sufficient to establish feasibility when the certificate declares \(P\le b<1\).

**A certificate must validate moments against the same support contract used by its extremal optimizer.** Otherwise, a generic feasibility check can accept moments for which the optimizer's declared distribution family is empty.

This review confirms the mathematical contract mismatch across the documented branches. It does not claim that a specific live execution path currently accepts such inputs: the feasibility helper's implementation and its runtime wiring still require direct verification.

## Mathematics: support-dependent variance bound

Let \(0\le P\le b\), with \(p=\mathbb E[P]\) and \(v=\operatorname{Var}(P)\). Since \(P^2\le bP\),

\[
\mathbb E[P^2]\le b\mathbb E[P]=bp.
\]

Therefore,

\[
v=\mathbb E[P^2]-p^2\le bp-p^2=p(b-p).
\]

The exact scalar feasibility conditions for a distribution on \([0,b]\) with specified mean and variance are

\[
0\le p\le b,\qquad 0\le v\le p(b-p).
\]

Sufficiency can be seen constructively: for \(0<p<b\), the point mass at \(p\) has variance zero, while a two-point distribution on \(\{0,b\}\) with mean \(p\) has variance \(p(b-p)\). Mixing these distributions preserves the mean and spans every variance between those endpoints. At \(p=0\) or \(p=b\), the only feasible variance is zero.

The generic bound \(v\le p(1-p)\) is weaker whenever \(b<1\) and \(0<p<b\), because

\[
p(1-p)-p(b-p)=p(1-b)>0.
\]

### Minimal counterexample

Take \(p=0.5\), \(b=0.6\), and \(v=0.1\). The generic condition passes because \(0.1\le0.25\), but the support-aware maximum is \(p(b-p)=0.05\). Thus no distribution supported on \([0,0.6]\) can have these moments.

The contradiction is not a numerical precision issue. It is a model-feasibility failure.

## Uncertain inputs: three-way result, not a guessed Boolean

When \((p,v,b)\) are intervals or belong to an uncertainty set \(\mathcal C\), the verifier must not silently plug in central estimates. Define the support-feasibility residual

\[
g(p,v,b)=v-p(b-p).
\]

A sound interval/robust procedure should return:

- **certified feasible** only when it establishes at least one admissible parameter triple and the contract's intended meaning is existential;
- **certified infeasible** only when every triple allowed by \(\mathcal C\) violates the support/domain conditions;
- **unresolved** when the uncertainty set includes both feasible and infeasible cases, or the analysis cannot decide.

For a claim that all parameter values are feasible, the gate is stronger: it must establish \(0\le p\le b\) and \(g\le0\) throughout \(\mathcal C\). Existential feasibility and universal feasibility are different predicates and must not share one status label.

Even a correct support-aware feasibility result only validates the moment constraints. It does not establish that the chosen support bound is physically justified, that the data-generating model is correct, or that a sampling interval has calibrated coverage.

## Great Scale mapping

| Level | Mathematics | Engineering interpretation | Required gate |
|---|---|---|---|
| 6801 | \(P^2\le bP\) on \([0,b]\) | Feasibility must use the optimizer's declared support | One shared support contract |
| 6810 | \(v\le p(b-p)\), not merely \(v\le p(1-p)\) when \(b<1\) | Prevent generic probability checks from admitting impossible bounded-support moments | Support-aware moment validator |
| 6820 | \(p(1-p)-p(b-p)=p(1-b)\) | The gap between generic and support-specific bounds is explicit and testable | Boundary and counterexample regression tests |
| 6830 | \(\exists (p,v,b)\in\mathcal C\) differs from \(\forall (p,v,b)\in\mathcal C\) | Preserve existential, universal, and unresolved semantics | Typed uncertainty-set contract |
| 6840 | Feasibility does not imply model truth or statistical coverage | Keep moment, support-provenance, and statistical statuses separate | Independent evidence gates |
| 6900 | Sharp optimization is meaningful only over a nonempty, correctly specified feasible set | Reject or mark unresolved before calculating extremal endpoints | Feasibility gate precedes optimization |

## Falsifiable tests

1. **Exact-boundary tests:** \(p=0\), \(p=b\), and \(v=0\) are feasible only with the required zero variance at the support endpoints.
2. **Generic-versus-bounded counterexample:** \((p,b,v)=(0.5,0.6,0.1)\) must fail support-aware feasibility although it passes \(v\le p(1-p)\).
3. **Tight-boundary test:** for several \(p\in(0,b)\), \(v=p(b-p)\) must be accepted as the maximum-variance boundary.
4. **Just-over-boundary test:** any \(v>p(b-p)\) must be rejected for exact inputs.
5. **Uncertainty semantics:** test uncertainty sets that are wholly feasible, wholly infeasible, and straddle the boundary; assert distinct outcomes.
6. **Contract consistency:** verify the same validated \(b\), \(p\), and \(v\) feed the feasibility check and the sharp-extremum routine; no duplicated or defaulted support value may silently diverge.
7. **Model caveat:** ensure a feasibility certificate cannot set support provenance or statistical coverage to “valid” without separate evidence.

## Repository integration boundary

- The risk/descent branch's README explicitly defines the sharp risk range for support \([0,b]\), exact moments, and a justified support gap.
- PR #92 describes an isolated exact-rational feasibility helper for the scalar probability-moment constraint under bounded uncertainty, with certified-feasible, certified-infeasible, and unresolved outcomes.
- The Great Scale bridge documentation describes readiness as software-invariant status only, not empirical, physical, or quantum evidence.
- This note specifies the shared mathematical contract and regression cases. It does not claim that the helper has been modified, that the risk sidecar is wired into the live state engine, or that hosted CI executed.

## Verification record

- **Mathematical checks executed in this review:** 4 exact arithmetic/assertion checks passed, including the counterexample above.
- **Repository inspection:** risk-branch README and lattice bridge fetched; the generic-versus-bounded contract gap is visible across the documented surfaces. Direct inspection of the feasibility helper's source and runtime call graph remains outstanding.
- **Repository tests/build:** not run in this review. Source presence, a local arithmetic check, and hosted CI are distinct evidence.
- **Science:** this is a probability/moment feasibility result, not a new physical law and not empirical confirmation of quantum geometry.
- **Promotion:** keep research-only until the actual helper and optimizer share one support contract, tests run on the exact candidate SHA, and logs/artifacts are inspectable.

## Conclusion

The new Great Scale invariant is:

**No extremal certificate before support-aware feasibility.**

The certificate should carry distinct fields for moment_feasibility_status, support_provenance_status, extremal_status, and statistical_status. A mathematically valid inequality is only useful when it is the inequality for the actual model being certified.
