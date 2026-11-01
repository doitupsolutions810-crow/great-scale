# Endomorphism Debate Atlas — research and integration contract

**Status:** interactive research instrument; not a scientific or production certification.
**Build:** 0.8.0 prototype on branch feat/endomorphism-debate-atlas-20261101.

## Why this layer exists

The Great Scale repository has grown from a ninefold symmetry visualization into a cross-layer research program: quotient-space semantics, involutions and contractions, coherence/mean projection, quantum-geometric scalar diagnostics, and evidence/promotion contracts. The UI should let a researcher change the map and immediately inspect consequences, while a multi-role council tries to falsify the current interpretation.

This is not simply a 3D graph. It is a map-and-witness laboratory: every result needs a domain, a transformation, an equivalence relation, a set of invariants, and a statement of what the plot cannot establish.

## Mathematical core

Let the ninefold circle be X = R / 9Z, with quotient map q(x) = [x]. A formula F on representatives induces a well-defined map F-bar on X only if x ~ y implies F(x) ~ F(y). That condition is distinct from continuity of F-bar.

The main experiment families are:

1. Reflection: R(x) = (9 - x) mod 9. On the continuous circle the fixed classes are [0] and [4.5]. On Z9, only 0 is fixed; the integer states form the pairs 1↔8, 2↔7, 3↔6, 4↔5.
2. Circle-native contraction: C_k(x) = [4.5 + k((x mod 9) - 4.5)]. For |k| < 1 the lifted affine map contracts toward 4.5. Fiber constancy is not a substitute for proving quotient continuity.
3. Heat: H(h) = h(1-h), with H(h)=H(1-h) and max 1/4. This scalar is many-to-one; it loses branch identity.
4. Mean projection: Qf = μ(f)1, μ(f) = (1/9)Σ f_j. Q²=Q and ker(Q) is the zero-mean subspace. Projection destroys recoverable detail.
5. Composition: compare R∘C_k and C_k∘R over the full domain, including seam representatives. Matching fixed points does not establish commutation.

## Research realization to test

A single scalar residual cannot be a complete state identity when the pipeline contains non-injective projection. Two distinct states can share a scalar while differing in signed orientation, topology, provenance, or authority. The research instrument therefore treats the following as separate channels:

- state/domain identity and quotient representative;
- transformation identity and composition order;
- signed orientation/topological channel;
- unsigned scalar/residual channel;
- numerical conditioning and error certificate;
- source revision, execution receipt and artifact digest;
- capability scope and authorization decision.

Candidate witness object:

    W = (domain, mapId, representative, quotientClass, signedChannel,
         scalarResidual, conditioning, sourceCommit, runReceipt,
         artifactDigest, capabilityScope, decision)

The candidate invariant is not that W is a new physical law. It is a software/research design rule: a lossy scalar is never used alone to reconstruct identity, certify execution, or authorize an action.

## Cross-repository architecture readback

The current inventory lists 38 repositories accessible to the connected GitHub account at the time of inspection, with a mix of public and private visibility. This atlas intentionally lists only selected public repositories; private repository names are not copied into the public Great Scale tree.

Integration-critical source readbacks reviewed for this build:

- Great Scale: quotient-seam findings, QGT scalar identifiability, GSLI residual bridge, evidence closure, and public integration registry.
- AVRONE: plan → parallel squad → lead merge; real tool/terminal boundary; replayable run logs. Open PR #14 defines a versioned cross-repository contract and explicitly keeps all integration edges unverified.
- Living Intermediate Control Plane: evidence envelope v1 proposal in PR #36 separates evidence validation from authorization, and distinguishes E0–E6 procurement readiness from G0–G6 production authorization.
- Capability Authority: PR #15 requires exact method-scoped rights and treats missing methods as non-matching; full test and caller migration remain required.
- CycleKernal: PR #13 addresses post-write acknowledgement ambiguity using stable idempotency keys and reconciliation; its focused isolated tests do not prove real MongoDB/Redis or hosted behavior.
- Grok Bot: recent commits fix Docker socket-proxy boot readiness. Boot success and live MCP/provider handshakes must be proven at runtime, not inferred from source.
- Cleanroom Agent System: repository history indicates vector memory, parallel orchestration, background agents, and deployment hardening.

This is a targeted cross-repository architecture pass, not a claim that every file, every branch, every commit, or every PR in all 35 repositories has been exhaustively reviewed. The open PR backlog in Great Scale alone is large. The next inventory pass must enumerate all PRs/branches and compare merge-base, head SHA, changed paths, and CI evidence before selecting additional integration work.

## Critical repository evidence

- Great Scale PR #129 adds a public-only repository map and promotion gate. It explicitly labels integration edges proposed/unverified and requires exact commit/run evidence before promotion.
- Great Scale PR #128 tracks projection/ledger divergence, stale writers, quotient continuity, and revision-bound verification.
- Great Scale PR #127 separates external side effects from evidence and acknowledgement. An error after a committed write does not prove that no effect occurred; retries require idempotency or reconciliation.
- Great Scale PR #126 defines four independent evidence obligations: integrity, authenticity, execution, and authority.
- Recent Great Scale CI runs have repeatedly reported runner_id=0 and empty step lists. Such runs are blocked/unknown; they are not test passes and do not demonstrate assertion failures.
- A previous QGT note overclaimed Richardson-based estimates as rigorous bounds. Later source audit explicitly corrected that claim: asymptotic estimates with a safety factor are not rigorous enclosures. Independent analytic/interval certification is required for certification-grade claims.

## Agent debate contract

The prototype exposes four distinct roles: algebraist, topologist, numerical analyst, and skeptic/falsifier. Its local deliberation is deterministic and visibly labeled as such. It does not impersonate connected LLM agents.

A live deployment should route these roles through AVRONE/Grok Bot with:
- bounded fan-out, timeouts, token and compute budgets;
- isolated, read-only repository inspection by default;
- explicit source/commit pins in every agent result;
- a lead that records agreement, disagreement, counterexamples, and unresolved proof obligations;
- tool execution only through capability-authorized adapters;
- append-only run receipts and durable idempotency;
- no self-promotion from agent-generated claims.

## Verification boundary

The current HTML uses browser-local computation and localStorage. It does not call GitHub APIs, execute code from repositories, connect to AVRONE, or send prompts to an LLM. Exported session JSON is a research log, not a signed evidence receipt.

Required before production:
1. run the repository's complete Node and Python suites from a clean checkout;
2. run browser interaction and accessibility tests against the exact commit;
3. verify exact-head CI with inspectable runner steps and logs;
4. connect the live agent backend using authenticated, method-scoped capabilities;
5. independently verify signed source/run/artifact receipts;
6. keep the promotion gate HOLD until the producer and consumer contracts match and end-to-end tests pass.


## Repository-scale audit snapshot — 2026-11-01

The connected GitHub account exposed 38 repository records. README access was attempted across the inventory; some repositories are empty or have no root README. The latest commit metadata was read for all 38 repositories, and the pull-request API was enumerated across the inventory. The API returned 275 pull-request records in total for this snapshot; Great Scale returned 125 PR records across two pages (121 open and 4 closed in the retrieved set). This covers PR metadata, not the complete diff/review discussion for every PR or the full historical commit graph of every repository.

The Great Scale branch API returned 130 branches across two pages. Every returned branch object reported protected=false; a direct read of main confirmed protected=false. The repository's current CI workflow is configured for push and workflow_dispatch, not pull_request. The latest inspected main commit is 2a87e3262e2106fc3ae58abf157335d1a44e8783 (2026-10-30), which changes CI to target a self-hosted runner labelled Great-Scale. The connector did not expose an inspectable Actions run for the atlas head; Vercel reported a successful preview status, which verifies deployment build status only, not the Node/Python test suite.

### System-level realization: the source graph is part of the experiment

A research claim cannot be tracked solely by its formula or its PR title. With many active branches and stacked PRs, the claim's actual meaning depends on the exact base SHA, head SHA, merge-base, changed paths, dependencies, and test evidence. Therefore, the mature Atlas should represent two coupled graphs:

- Mathematical graph: domains, maps, compositions, quotient relations, invariants, counterexamples and proof obligations.
- Source/evidence graph: repository, branch, commit, merge-base, PR, workflow run, runner, command, result artifact, signer and authorization scope.

The join between these graphs must be revision-bound. A proof or test on one branch does not automatically validate another branch; a Vercel success does not imply the mathematical or test contract passed. Main branch protection and a PR-triggered test path are high-priority governance improvements, but this Atlas PR does not change branch settings or CI triggers.


## Live AVRONE bridge implementation — 2026-11-01

The companion AVRONE implementation is being proposed separately in branch
`feat/great-scale-live-research-bridge-20261101`. When reviewed and deployed, the Atlas
can run the live council from a same-origin AVRONE host at `/static/atlas.html`.

- `POST /api/research/debate` validates the repository/commit format, resolves the exact
  full SHA through the public GitHub commit API, and refuses an unavailable or mismatched source.
- The endpoint runs AVRONE's existing multi-agent `deep` path with four reviewers and 1–3
  bounded rounds, then records a JSON receipt under the configured AVRONE data directory.
- `GET /api/research/receipts/{run_id}` retrieves the stored receipt through the same local/admin
  access policy as other privileged run routes.
- The receipt binds repository, exact commit SHA, run ID, claim, run mode, requested rounds, and
  SHA-256 of the recorded result. It is an integrity record, not a digital signature, theorem, or
  independent validation of the model output.
- The browser never stores or sends an admin token. Local loopback access works under the
  default policy; remote deployments must use the existing authenticated path or a properly
  configured same-origin authentication proxy. Do not set `AVRONE_PUBLIC_ACCESS=all` just to
  make the panel work.
- GitHub commit identity is checked server-side. The endpoint does not execute repository code
  or claim to have run the repository test suite. Agent output must say when source files were
  not actually retrieved or tests were not executed.
- Verification remains pending until the AVRONE PR's CI and integration tests pass on its exact
  head SHA and a real deployment demonstrates a successful authenticated run plus receipt retrieval.


### Ingestion and receipt refinement

The AVRONE draft now fetches the GitHub commit object and a bounded set of repository-relative text files at the exact SHA before dispatch. By default it requests the Atlas HTML, this research contract, the Atlas contract test, and `package.json`; callers may provide up to five paths. File contents are bounded to 30,000 characters total and each fetched item records its Git blob SHA and truncation status. The receipt includes those source excerpts and the complete recorded council result in the SHA-256 digest envelope, subject to a 2 MB result cap. No fetched file is executed.

A server-side `GITHUB_TOKEN` may be configured for authenticated GitHub API access when required; it must remain in the server environment and never be sent to the browser. Use a least-privilege token and keep the default local/admin access boundary. Exact commit lookup or source fetch failures fail closed.
