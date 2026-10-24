# Descent XCVII — Orthogonal evidence closure

**Status:** cross-repository design result with executable mathematical regression checks. This is not a new physical law or an empirical claim.

## Finding

Great Scale's scalar channels are useful summaries, but they are non-injective projections of richer state. They must not be treated as proof of identity, authorization, provenance, or execution safety.

For a valid two-direction pure-state quantum geometric tensor (QGT), let
\[
\det Q=\det g-\frac{F_{12}^2}{4},\qquad
\chi=\frac{|F_{12}|}{2\sqrt{\det g}},\qquad
R=\frac{\det Q}{\det g}=1-\chi^2.
\]
Great Scale embeds this residual through
\[
S_Q=\operatorname{heat}\!\left(\frac{1+\chi}{2}\right)
=\frac{1-\chi^2}{4}=\frac{R}{4},\qquad
\Psi_Q=\mathrm{CONE}+S_Q.
\]

Two distinct losses follow directly from the equations:

1. **Orientation loss:** replacing \(F_{12}\) with \(|F_{12}|\) means \(F_{12}\) and \(-F_{12}\) yield the same \(\chi\), \(S_Q\), and \(\Psi_Q\), despite opposite curvature orientation.
2. **Scale loss:** the simultaneous rescaling \((g,F)\mapsto(cg,cF)\), \(c>0\), preserves \(\chi\) and \(S_Q\). Absolute metric scale is not recoverable from this scalar channel. The determinant ratio also does not encode the full metric anisotropy.

This is not a defect in the scalar's intended role. It is a precise statement about what the scalar does not contain.

## General mathematical principle

Let \(X\) be the full state and \(P:X\to Y\) a scalar projection. If \(P\) is non-injective, then different states can share one projected value. A downstream decision \(A:X\to\{0,1\}\) can be represented as a function of \(P(X)\) only if \(A\) is constant on every fiber \(P^{-1}(y)\).

Identity, audience, rights, expiry, revocation, and provenance are not determined by \(S_Q\), \(\Psi_Q\), heat, belief, or a readiness score. Therefore **authorization must not be derived from Great Scale's scalar state**.

## Cross-repository evidence

- **Great Scale:** QUANTUM_GEOMETRY_BRIDGE.md defines the QGT scalar and documents orientation, scale, and anisotropy information loss. public/quantum-geometry.cjs returns numerical diagnostics separately from the scalar.
- **Capability Authority:** plane_service/core.py issues structured capabilities with issuer, audience, rights, constraints, timestamps, expiry, nonce, trust domain, policy version, and delegation metadata. plane_service/executor.py checks signature, bounds, capability validity, revocation state, and rate limits before returning a signed receipt.
- **Living Intermediate Control Plane:** docs/avrone-stack-integration.md says the lattice observation bridge does not open either execution gate; observations and evidence remain separate.
- **TrainLLM contrast:** src/auth.ts signs an HS256 JWT containing a capability claim without specifying expiresIn; src/server.ts exposes POST /token and falls back to dev-secret when JWT_SECRET is unset. In the code reviewed, that route has no authentication middleware. If this server is reachable in that configuration, a caller can obtain a token that passes the fixed scale-sla capability check. Treat this as a security finding requiring a separate remediation, not as a property of Great Scale itself.

A related authorization detail needs review in Capability Authority: plane_service/core.py::verify checks right type and resource but does not compare method, even though attenuation compares (type, resource, method). Callers should not assume method-level enforcement until the verifier is corrected and covered by a regression test. This note records code behavior, not a claim that every deployment exposes the same path.

## Orthogonal evidence model

Keep the channels explicit:
\[
X=(G,I,C,E)
\]
where:

- \(G\): geometric state and numerical diagnostics;
- \(I\): authenticated workload identity;
- \(C\): signed, scoped capability claims;
- \(E\): provenance and execution receipts.

Great Scale may project \(G\) to \((S_Q,\Psi_Q)\), but it must not collapse \(I,C,E\) into that projection. A useful action gate is a conjunction of independently verified predicates:
\[
\Gamma=
V_{\mathrm{sig}}\land V_{\mathrm{id}}\land V_{\mathrm{aud}}
\land V_{\mathrm{right}}\land V_{\mathrm{constraints}}
\land V_{\mathrm{time}}\land V_{\mathrm{policy}}\land V_{\mathrm{revocation}}.
\]
A missing or failed required predicate denies the action. In particular, a right check should bind the operation, resource, and method; a capability should be rejected at or after its expiry; and any receipt should refer to the exact capability and action. This is a design invariant, not a claim that every repository currently implements every term correctly.

## Mapping to the Great Scale

**System 21 — Binding layer.** The state \(B\) carries relations and their residuals; a binding is not itself proof that a downstream claim is true.

**System 22 — Complementary Projection Closure.** For an involution \(\sigma^2=I\), define
\[
P_\pm=\frac{I\pm\sigma}{2},\quad
P_\pm^2=P_\pm,\quad P_+P_-=0,\quad P_++P_-=I.
\]
These project complementary components without pretending that either projection contains the whole state.

**System 23 — Orthogonal Evidence Closure.** Apply the same discipline across trust domains: geometry, identity, authority, and evidence remain distinct typed channels. They may be correlated by a trace/capability identifier, but no channel silently substitutes for another. A scalar is an observation, a signature is an integrity/authenticity check, an identity binds a workload, a capability limits authority, and a receipt records an outcome.

The chain becomes:
\[
1\to2\to\text{relation}\to\text{quotient}\to\text{symmetry}
\to\text{geometry}\to\text{invariant}\to\text{information}
\to\text{constraint}\to\text{coherence}\to\text{projection}
\to\text{evidence}\to\text{capability}.
\]

The existing cone law remains unchanged:
\[
0\le S_Q\le\frac14,\qquad
\Psi_Q=\phi^{-2}+S_Q\ge\phi^{-2}\approx0.381966.
\]
The trust gate \(\Gamma\) is discrete and independent of this scalar range; a high or stable \(\Psi_Q\) never means “authorized.”

## Mathematics, science, and limits

- **Mathematics:** non-injectivity and the sign/scale invariances above follow algebraically from the definitions.
- **Computation:** test_evidence_projection.py checks orientation loss, common-scale invariance, the cone floor, QGT-bound rejection, and the fact that equal scalar summaries can accompany different rights.
- **Security engineering:** repository inspection finds concrete authentication and method-check gaps; these require code-level fixes and their own tests.
- **Science:** no empirical physical claim follows from this mapping. It is a formal bridge between mathematical observables and safe system architecture.

## Verification

~~~bash
npm test
python3 test_descent.py
python3 test_evidence_projection.py
npm run all
~~~

The added checks are deterministic and use only the Python standard library. A local clone could not be fetched in this execution environment, so the pre-existing full Great Scale suite has not been claimed as locally passing. GitHub Actions should be used to verify the branch; recent repository CI runs have failed before runner steps were assigned, so a red status without executed steps is not evidence of a test assertion failure.
