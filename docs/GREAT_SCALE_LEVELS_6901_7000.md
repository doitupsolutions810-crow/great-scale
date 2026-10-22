# Great Scale — Levels 6901–7000: certificate composition and support identity

## Profound finding

Direct source inspection resolves the earlier uncertainty: the risk optimizer in PR #91 already enforces the support-aware variance bound, but the exact-rational feasibility helper in PR #92 certifies a different, broader model. The two components are mathematically compatible only when the declared support is the full interval \([0,1]\); they are not interchangeable for a bounded support \([0,b]\) with \(b<1\).

This is a **verified cross-branch interface gap**, not evidence that the PR #91 optimizer itself omits its variance guard, and not proof of a live production defect. Neither research component is wired into a single end-to-end state-engine path in the inspected source.

## Source-grounded observations

1. **PR #92 helper** (\`robust_feasibility.py\`) clips the uncertain mean to \([0,1]\) and certifies
   \[
   0\le p\le1,\qquad v\ge0,\qquad v\le p(1-p).
   \]
   Its API has no support maximum \(b\) or support gap \(\delta\); its result therefore cannot certify compatibility with an arbitrary narrower support.

2. **PR #91 extremal optimizer** (\`public/risk-certificate.js\`, \`computeMomentLogLossBound\`) computes \`supportMaximum = 1 - supportGap\` and rejects variance outside
   \[
   0\le v\le p(b-p),\qquad b=1-\delta.
   \]
   This is the correct support-aware guard for its declared support.

3. **The interfaces do not compose.** The helper's \`certified_feasible\` status is not passed to the optimizer, the helper cannot receive the optimizer's support contract, and the empirical \`computeRiskCertificate\` path does not consume the moment helper's certificate. The inspected source therefore contains individually useful sidecars, not a unified proof-carrying pipeline.

4. **Hosted CI is not green evidence.** For the exact PR #91 head \`7b966c2893dcffc905badec8e491a49511d090d8\` and PR #92 head \`618f42bda22a773952ed685fe5ce8b35afb33f3f\`, the available GitHub Actions runs report failure and their job payloads have empty step lists. These records do not establish that test assertions ran or failed. Do not substitute the PR #91 description's claimed local test counts for independently inspectable logs.

## Mathematics: one support identity, one certificate contract

For \(P\in[0,b]\), \(p=\mathbb E[P]\), and \(v=\operatorname{Var}(P)\), use \(P^2\le bP\):
\[
\mathbb E[P^2]\le bp
\quad\Longrightarrow\quad
v=\mathbb E[P^2]-p^2\le p(b-p).
\]

The difference from the generic constraint is
\[
p(1-p)-p(b-p)=p(1-b).
\]
For \(0<p<b<1\), this is strictly positive. Thus the generic helper may certify a point that is impossible under the optimizer's support.

### Minimal executable-by-hand witness

Take \(p=0.5\), \(v=0.1\), \(b=0.6\) (\(\delta=0.4\)):
\[
v=0.1\le p(1-p)=0.25
\]
so the PR #92 generic constraint passes, while
\[
p(b-p)=0.5(0.1)=0.05<0.1=v.
\]
The PR #91 bounded-support optimizer must reject this pair. This is a concrete demonstration that a generic pre-check is not a valid pre-check for the narrower optimizer.

## Great Scale mapping

| Level | Mathematical invariant | Engineering interpretation | Verification gate |
|---|---|---|---|
| 6901 | \(b=1-\delta\) is part of the model, not display metadata | Support is a first-class typed input | Reject missing or mismatched support |
| 6910 | \(v\le p(b-p)\) | One support-aware feasibility predicate governs bounded moments | Boundary and just-over-boundary tests |
| 6920 | \(p(1-p)-p(b-p)=p(1-b)\) | Generic feasibility can be a false positive for the bounded model | Regression on \((p,v,b)=(0.5,0.1,0.6)\) |
| 6930 | \(\text{certificate.model}=\text{optimizer.model}\) | A certificate must bind to the exact support, moments, objective, and version | Compare canonical contract hashes or immutable input records |
| 6940 | \(\text{feasible}\not\Rightarrow\text{support justified}\) | Mathematical feasibility is distinct from support provenance and statistical coverage | Independent status fields and evidence |
| 6950 | \(\text{generic precheck}\not\Rightarrow\text{bounded feasibility}\) | A green status from PR #92 cannot authorize PR #91's optimizer | Require the same support-aware validator |
| 7000 | No optimization before a compatible feasibility proof | Compose validator → optimizer → witness verifier → evidence/status envelope | End-to-end exact-head test and inspectable CI logs |

## Required integration contract

The next implementation should define one versioned request object containing:
- \`mean\`, \`variance\`, and \`supportMaximum\` (or \`supportGap\`, never both ambiguously);
- uncertainty bounds and their semantics (existential feasibility versus universal feasibility);
- objective/version and arithmetic policy;
- support-provenance status, statistical status, and source-input identity.

The support-aware validator should return a typed result with the exact normalized inputs and margins. The optimizer must accept that validated object (or independently recompute and compare the same invariant), then emit extremal witnesses. A witness checker should recompute total mass, mean, variance, support membership, and objective value. Do not let a generic \`certified_feasible\` flag flow into a narrower-support optimizer.

Suggested status separation:
- \`moment_feasibility_status\`
- \`support_provenance_status\`
- \`extremal_status\`
- \`statistical_status\`
- \`source_binding_status\`

## Test / verify / run record

- **Source inspection:** fetched the PR #92 exact-rational helper and tests, PR #91 risk optimizer and descent sidecar, package scripts, and the PR metadata.
- **Mathematical witness:** checked by direct arithmetic that the generic constraint passes and the bounded-support constraint fails for the example above.
- **Optimizer source:** contains the support-aware variance guard; no defect claimed for that guard.
- **Repository tests/build:** not run locally in this review.
- **Hosted CI:** both exact PR heads have reported failed runs with empty job step arrays; test execution/result is therefore unverified, not a confirmed test failure.
- **Deployment:** Vercel reported a deployment quota limit; that is a deployment-resource issue, not evidence about mathematical correctness or test results.
- **Science boundary:** this establishes a probability-moment model contract. It is not empirical evidence for a physical or quantum claim.

## Conclusion

**The profound finding is a certificate-composition gap: the two components are locally defensible under different contracts, but a certificate is not portable across models unless it binds to the same support and exact inputs as the optimizer.**

Keep both PRs research-only until the support-aware contract is shared, the witness checker is exercised, and CI logs from the exact candidate SHA are inspectable.
