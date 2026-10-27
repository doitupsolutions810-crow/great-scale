# Descent XCV — Spherical assembly evidence contract

Status: research/engineering contract; no physical interlock claim is certified by this note.

## Finding

A compact invariant is not a complete state description. The Great Scale topological scalar is invariant under sign reversal of the Chern number and common positive rescaling of signed and absolute curvature. Therefore, equal scalar values do not imply equal orientation, equal magnitude, equal geometry, equal provenance, or equal authorization.

For a gapped pure two-band reference model, define

\[
\mathcal A_Q=\frac{1}{2\pi}\int_{\mathrm{BZ}}|F_{12}|\,d^2k,\qquad
C=\frac{1}{2\pi}\int_{\mathrm{BZ}}F_{12}\,d^2k.
\]

The triangle inequality implies \(|C|\leq\mathcal A_Q\). When \(\mathcal A_Q>0\),

\[
\eta_T=\frac{C}{\mathcal A_Q},\qquad
S_T=\frac{1-\eta_T^2}{4},\qquad
\Psi_T=\phi^{-2}+S_T.
\]

Since \(S_T\) depends on \(\eta_T^2\), the transformation \(C\mapsto-C\) preserves \(S_T\) and \(\Psi_T\). A common positive scaling of \(C\) and \(\mathcal A_Q\) also preserves the ratio. This is an algebraic property of the mapping, not a new physical law.

## Great Scale mapping

Keep the following evidence channels distinct:

| Channel | Meaning | Acceptance rule |
|---|---|---|
| \(\Psi_T,S_T\) | Compact scalar diagnostic | Recompute from the source tuple; never treat as a full state identity |
| \(C\) | Signed topological orientation | Preserve sign and orientation convention |
| \(\mathcal A_Q,E_Q\) | Absolute geometric magnitude and excess | Require \(\mathcal A_Q\geq|C|\), \(E_Q=\mathcal A_Q-|C|\) |
| Numerical residuals | Convergence and arithmetic evidence | Measure every configured gate; no heuristic flag alone certifies convergence |
| Geometry evidence | Contacts, clearance, penetration, rigidity | Measure from canonical surfaces/solids; graph adjacency is not contact proof |
| Provenance | Source revision and artifact identity | Bind results to commit, input digest, runtime and exact command |
| Execution | Build/test outcome | Record exit status and full output independently of scientific validity |

The scalar must not replace or silently mutate existing phase-driven state.

## Spherical seed reconciliation blocker

Two current prototype artifacts encode different seed counts:

- PR #111 CommonJS/UMD seed: 74 vertices and 127 edges by source structure.
- Standalone ESM archive baseline: 86 vertices and 143 edges.

These counts must not be reconciled by guesswork. Until the authoritative CAD mesh or a dimensioned source image is supplied, both are provisional reconstructions. The Grok project URL was not retrievable in the available environment, so its contents are not evidence for choosing either seed.

Required canonicalization steps:

1. Select an authoritative source mesh or a dimensioned, versioned reconstruction.
2. Define units, coordinate frame, handedness, vertex/edge/face semantics, and schema version.
3. Add exact count and semantic regression tests for the canonical seed.
4. Define each rigid transform \(\mathbf x_{ij}=\mathbf p_i+R_i\mathbf v_j\), with \(R_i\in SO(3)\).
5. Compute surface-to-surface distance, penetration depth, minimum clearance, and contact tolerance separately.
6. Test mechanical rigidity/stability only after geometry, material assumptions, constraints, and load cases are specified.
7. Compare Fibonacci shell, staggered rings, nested shells and volumetric fill under the same seed, scale and evaluation criteria.

A nearest-neighbor graph can report connectivity while surfaces remain separated or interpenetrate. It is therefore only a graph diagnostic.

## Verification protocol

### Algebraic property tests

For representative valid tuples and random positive pairs \((P,N)\), verify:

\[
C=P-N,\quad \mathcal A_Q=P+N,\quad
\frac{1-(C/\mathcal A_Q)^2}{4}=\frac{PN}{(P+N)^2}.
\]

Verify sign symmetry by comparing \((C,\mathcal A_Q)\) with \((-C,\mathcal A_Q)\): scalar outputs must match while the signed channel must flip. Verify scale symmetry by multiplying both inputs by a positive representable factor. Handle \(\mathcal A_Q=0\) explicitly; the ratio is undefined and must not be fabricated.

### Geometry tests

- Canonical seed counts and topology match the versioned specification.
- Rigid transforms preserve all pairwise distances within numerical tolerance.
- No accepted placement exceeds the specified penetration tolerance.
- Every claimed contact has measured surface distance within a declared contact tolerance.
- Clearance and contact are reported separately; graph edges do not stand in for contact.
- Each placement mode is evaluated on the same geometry and deterministic seed.

### Repository/build evidence

Run from a clean checkout on the exact candidate SHA:

```bash
npm test
python3 test_descent.py
npm run all
```

Record commit SHA, runtime versions, exact commands, exit codes, complete output, and artifact digests. The standalone prototype's local 9/9 ESM and 8/8 CommonJS checks are not a substitute for these repository-wide runs. The observed hosted CI failures had no recorded steps and unavailable logs; their cause remains unresolved.

## Evidence boundary

This note establishes algebraic properties and an engineering acceptance contract. It does not certify the spherical shape's physical interlock, mechanical stability, a new physical law, or the contents of the inaccessible Grok project. Those claims require the missing source geometry and repeatable tests against a canonical candidate.


## Descent XCV addendum — CI observability and test coverage

A deeper inspection of the current `main` CI workflow found a separate integration gap:

- `.github/workflows/ci.yml` runs only `npm test` and `python3 test_descent.py`.
- `package.json` defines `npm test` as `node test.js && node test_quantum_geometry.js && node test_topological_qgt.cjs`.
- The spherical prototype's standalone CommonJS/ESM tests are not included in those scripts. Their local pass counts therefore do not imply they are exercised by repository CI.
- The observed workflow run for this evidence-contract PR completed as failure in about three seconds with `runner_id: 0`, an empty `steps` array, and no runner name. This is consistent with failure before normal job execution; it does not identify the underlying platform cause and is not evidence that a particular test assertion failed.

### Required CI repair and acceptance

1. Diagnose the hosted runner/check initialization failure from GitHub-side diagnostics; do not classify it as a code failure without logs.
2. Add the canonical spherical test command to the repository test script only after its test path is committed and deterministic.
3. Ensure the workflow reports named checkout, setup, test, and descent steps.
4. Confirm the exact candidate SHA ran every step and retain full output and exit codes.
5. Treat CI coverage as incomplete until the spherical tests are part of the normal test entry point and a real runner executes them.

This is an important evidence distinction: a test that passes locally but is not wired into the repository test command is not a regression guard for future commits. A CI job that never reaches its steps is an observability/runner failure until demonstrated otherwise.
