# Great Scale — Descent CLXXV: freshness is not connected until the producer and revision are connected

## Finding

The cross-repository assurance chain had a concrete integration seam: the control-plane's overlapping authorization PRs were on the same base but carried different evidence-contract versions. PR #29 had moved the evidence-console validator to v5.4.0 with source-issued timestamps; PR #31 still expected v5.3.1 while adding shared procurement authorization and signed supply-chain report verification. A consumer branch could therefore remain stricter about authorization while still accepting evidence without source-issued freshness.

The v5.4.0 validator and its dedicated contract tests have now been ported into PR #31's shared-authorization/supply-chain branch. This connects the freshness predicate to the branch with the stronger procurement policy. It does not establish that the production producer emits the new contract.

## Verified branch observations (2026-10-27)

| Component | Observed revision / run | Result | What it proves |
|---|---|---|---|
| Living Intermediate Control Plane PR #31 | `a43c3568db06e4ec45c038965b98bc7ed9097d3c` plus documentation commit `4afbf7aded37d0f52e794d4ad547b8cd823f60f5` | CI run [40430008486](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40430008486) failed; job logs/steps unavailable | Freshness code/tests are committed; full suite outcome is unknown because the failure cannot be diagnosed from returned logs |
| Living Intermediate Control Plane PR #29 | `58a0cac2a79fad2d4a82d3c3950628aee2f9a956` | Open draft; overlapping changes noted in PR body | It contains the original v5.4.0 freshness change; do not merge overlapping branches independently without consolidation |
| Capability Authority PR #12 | `dd8c4e38136d3e3e81891045be0ace216a6c5253` | Run [40429217283](https://github.com/doitupsolutions810-crow/capability-authority/actions/runs/40429217283) failed in both `test` and `slim-probe`; logs unavailable | No qualifying test pass can be claimed |
| Great Scale PR #128 | `c47473aaa87334fc291fb34ae6a6eb04d3b702fb` | Run [40429275987](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40429275987) failed; job logs unavailable | The aggregate does not currently provide revision-bound passing evidence |
| Local isolated freshness model | Exact policy reproduced from the v5.4.0 validator | 10/10 scenarios passed | Model behavior only; not execution of committed repository tests |

The repeated `BlobNotFound` responses mean the failure causes remain unidentified. Do not classify them as source-code failures or runner-startup failures without the missing step evidence.

## Mathematical contract

For a candidate revision (R), evidence (E), decision time (t), and policy (P):

[
\operatorname{Accept}(R,E,t,P)=
\operatorname{Policy}(P)
\land \operatorname{Complete}(E)
\land \operatorname{Authentic}(E)
\land \operatorname{Fresh}(E,t)
\land \operatorname{Reach}(T,C)
\land \operatorname{Execute}(T,R)
\land \operatorname{Bound}(R)
\land \operatorname{Pass}(R)
]

The freshness predicate is:

[
\operatorname{Fresh}(E,t)=
\operatorname{Parse}(g)\land\operatorname{Parse}(x)
\land g\leq t+30s
\land t-g\leq 5min
\land x>t
\land 0<x-g\leq 5min
]

where (g) and (x) are source-issued generation and expiry timestamps. The client probe time is diagnostic and does not appear in the predicate.

Three distinctions remain mandatory:

1. Freshness is not authenticity: the producer can forge its own timestamps unless identity/signature is independently verified.
2. Authenticity is not completeness: signed evidence can still omit events; a sequence watermark and independent checkpoint may be required.
3. A passing model is not executed source: required repository tests and hosted CI must pass on the exact reviewed candidate.

## Mitigation integrated

- PR #31 now uses the v5.4.0 evidence-console validator and includes `test/evidence-console.test.mjs` in the canonical `npm test` command.
- `docs/evidence-contract-v5.4.0.md` defines the live-production acceptance gate and explicitly distinguishes freshness, authenticity, and completeness.
- PR #29's body now records the overlap, and PR #31's body records the port. Both remain draft/unmerged; avoid merging the same logical change twice.
- The isolated model was corrected to expect overlapping stale/lifetime failure reasons, then passed 10/10 cases.

## Last unconnected dependency: the actual producer

The status/schema producer for the public evidence endpoint has not been identified and live-verified from the accessible repository evidence in this pass. The v5.4.0 contract requires the producer to refresh source timestamps from actual readiness observations; a timestamp baked into a static artifact will expire. The consumer must remain fail-closed until a live probe proves that both production endpoints meet the v5.4.0 contract.

## Acceptance decision

[
\boxed{\text{HOLD} \quad \text{because } \operatorname{Execute}(T,R),\operatorname{Bound}(R),\operatorname{Pass}(R),\operatorname{Authentic}(E)\text{ remain unproven}}
]

The next step is not another blind retry. Recover usable Actions logs or reproduce each canonical suite on a trusted clean checkout; separately identify and test the live producer and bind its output to a verifiable source identity and freshness contract. Only then can the cross-repository chain be accepted.
