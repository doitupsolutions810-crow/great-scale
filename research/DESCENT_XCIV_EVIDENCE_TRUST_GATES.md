# Descent XCIV — Geometry, evidence, and authority

## Main finding

The Great Scale scalar is a normalized measure of curvature-orientation cancellation, not a complete certificate of topology, geometry, provenance, or permission to act.

For a converged, gapped, pure two-band model, define

\[
\mathcal A_Q=\frac{1}{2\pi}\int_{\mathrm{BZ}}|F_{12}|\,d^2k,
\qquad
C=\frac{1}{2\pi}\int_{\mathrm{BZ}}F_{12}\,d^2k.
\]

The triangle inequality gives

\[
\boxed{\mathcal A_Q\ge |C|}.
\]

Define the geometric excess and its normalized form

\[
E_Q=\mathcal A_Q-|C|,
\qquad
e=\frac{E_Q}{\mathcal A_Q},\quad \mathcal A_Q>0.
\]

Then \(|C|/\mathcal A_Q=1-e\), and the established Great Scale topological correction becomes

\[
S_T=\frac{1-(C/\mathcal A_Q)^2}{4}
=\frac e2-\frac{e^2}{4},
\]

\[
\boxed{\Psi_T=\phi^{-2}+\frac e2-\frac{e^2}{4}},
\qquad \phi=\frac{1+\sqrt5}{2}.
\]

This is an algebraic reparameterization of the existing correction, not a new physical law.

## What the scalar cannot tell us

1. **Orientation:** \(C\mapsto-C\) leaves \(\Psi_T\) unchanged.
2. **Absolute scale:** common positive scaling of \(\mathcal A_Q\) and \(C\) leaves \(e\) and \(\Psi_T\) unchanged.
3. **Evidence provenance:** a numerically consistent tuple does not prove which source, commit, runtime, or artifact produced it.
4. **Authorization:** a correct scientific result does not grant permission to perform an operation.

Keep the tuple \((C,\mathcal A_Q,E_Q,\tau,\Psi_T)\), numerical residuals, model assumptions, and provenance references separate. When \(\mathcal A_Q=0\) and \(C=0\), the ratio \(C/\mathcal A_Q\) is undefined; do not assign a polarization-derived scalar.

## Great Scale mapping

| Great Scale channel | Evidence-system meaning | Required invariant |
|---|---|---|
| \(S_T\) and \(\Psi_T\) | Compact geometric diagnostic | \(\Psi_T\ge\phi^{-2}\) and scalar agrees with the signed/absolute tuple |
| \(C\) | Signed topology | Preserve orientation; do not infer it from \(\Psi_T\) |
| \(\mathcal A_Q\), \(E_Q\) | Absolute geometry and excess | \(\mathcal A_Q\ge|C|\), \(E_Q=\mathcal A_Q-|C|\) |
| Refinement, grid-origin, cancellation, entropy residuals | Numerical evidence | All configured gates must be measured and pass before numerical acceptance |
| Source commit and artifact digest | Reproducibility/provenance | Bind claim to exact source and canonical artifact bytes |
| Scoped capability, audience, operation, expiry | Authorization | Validate independently of scientific correctness |
| Exit code and immutable receipt | Execution outcome | Successful execution is not implied by a valid formula or an authorization decision |

The evidence chain is additive to the existing phase-driven Great Scale state; it must not replace or silently mutate the canonical state channel.

## Control-plane acceptance invariant

An envelope must not be treated as accepted merely because it contains `acceptance: "accepted"`. A trusted consumer should require independent gates:

- domain/model assumptions valid;
- converged numerical outputs and measured residuals;
- exact source and artifact provenance verified;
- digest/signature cryptographically verified by a trusted verifier;
- capability issuer, scope, audience, operation, expiry, and revocation state verified;
- execution result reconciled and an immutable receipt recorded.

The Living Intermediate Control Plane's proposed validator now checks the envelope's arithmetic and the *presence/shape* of authorization evidence for accepted claims. It does **not** itself verify cryptographic signatures, authenticate capability issuers, prove provenance, check revocation, or implement the end-to-end receipt path. Those checks must remain in a trusted integration layer.

## Verification status

- The focused evidence-validator harness was run in an isolated Node environment: **14/14 tests passed** against a local reconstruction of the current validator and focused tests.
- The complete Living Intermediate Control Plane suite (`cd platform && npm test`) has not been run.
- The current hosted Plane CI run failed with no recorded steps; log retrieval returned `BlobNotFound`. The cause is unresolved, so this is neither a passing CI result nor proof of a test assertion failure.
- Great Scale's own `npm test`, `python3 test_descent.py`, and `npm run all` were not run as part of this change.
- No physical or empirical claim is established by this algebraic and contract-level work.

## Required next proof

Execute both repositories' full test suites on the exact candidate commits, verify the artifact digest and signature in a real trusted verifier, test expired/wrong-audience/revoked capabilities, and exercise producer → validator → authorization → immutable receipt with failure injection. Until then, the integration is a research/engineering contract, not production authorization.
