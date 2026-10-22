# Great Scale Levels 5301–5400: Attestation Validity, Revocation, and Trust Epochs

**Track:** `research/kernel-hardening-4401-4500`  
**Scope:** design and assurance semantics for the proof-kernel promotion gate  
**Implementation status:** research specification only; this document does not add signature verification, a trusted collector, or revocation enforcement to `promotion_gate.js`.

## 1. Descent result

Levels 5201–5300 established the trust-boundary distinction: a JSON field cannot authenticate the process that produced it. The next descent reveals a second distinction:

> **Authenticity is not timeless, and integrity is not authority.**

A valid signature establishes a cryptographic relation between signed bytes and a key, under a specific algorithm and verification procedure. It does not by itself establish that the key was authorized for this repository, workflow, artifact type, candidate commit, or decision; that the key was not revoked; that the evidence is fresh; or that the PR still points to the attested source.

An attestation must therefore be evaluated against an explicit trust policy at the time it is used. A signature that was valid at issuance may be inadmissible at promotion time.

## 2. Mathematical model

Let:

- (e) be the evidence payload;
- (sigma) be its signature;
- (k) be the key identity and public-key material;
- (P_t) be the verifier's trust policy at decision time (t);
- (c) be the requested context (repository, workflow identity, PR number, candidate SHA, and intended action);
- (t_i) be the claimed issuance time and (t_x) the expiry time;
- (r_t) be the revocation state known to the trusted verifier at time (t).

Define admissibility as the conjunction

[
A(e,\sigma,k,P_t,c,t) =
C(e) \land S(e,\sigma,k) \land I(k,P_t,t)
\land B(e,c) \land F(e,t) \land R(k,r_t,t)
\land N(e,c,t).
]

The predicates mean:

- (C): the payload has an unambiguous, strictly validated schema and canonical signing representation;
- (S): the cryptographic signature verifies using an explicitly permitted algorithm and key;
- (I): the issuer and key are authorized by the verifier-controlled policy for this purpose at time (t);
- (B): repository, workflow, run, receipt, artifact, PR, and full candidate SHA bindings are mutually consistent;
- (F): freshness checks pass, including an allowed issuance/expiry window and bounded clock-skew policy;
- (R): key and issuer status passes revocation / compromise policy at verification time;
- (N): replay resistance and action-time state checks pass.

The promotion gate may only claim authenticated admissibility when every required predicate has been established by trusted mechanisms. If only schema checks and cross-field comparisons are implemented, the result is **structurally eligible for further review**, not authenticated and not safe to promote.

### Time-indexed validity

Define (A_t=A(e,\sigma,k,P_t,c,t)). In general,

[
A_{t_0}=\mathrm{true} \centernot\Rightarrow A_{t_1}=\mathrm{true}.
]

This is not a defect in cryptography. The policy, PR head, revocation state, artifact availability, or acceptance window may legitimately change between (t_0) and (t_1). The verifier must reevaluate decision-time conditions rather than treating a prior green result as a perpetual capability.

### Policy monotonicity under uncertainty

For a high-assurance promotion decision, missing or unverifiable trust state must not increase privilege. Let (U) denote unavailable or ambiguous evidence about issuer status, revocation, or current PR state. The safe policy is

[
\operatorname{Admit}(e\mid U)=\mathrm{false}
]

for checks designated mandatory by the trust policy. This is a fail-closed design requirement, not a claim that every low-risk workflow must reject all transient outages; exception behavior must be explicit, bounded, and auditable.

### No self-authenticating provenance

If two sources supply byte-identical payloads, a deterministic payload-only validator cannot infer which source produced them. Therefore origin authentication requires an external trust anchor or authenticated collection channel; a payload's self-declared `source`, `verified`, `issuer`, or `trusted` fields cannot substitute for that mechanism.

## 3. Revocation, rotation, and replay model

A future authenticated envelope should bind, at minimum, a versioned schema, issuer identity, key identifier, algorithm identifier, canonical payload digest, repository identity, workflow identity, run identity, full commit SHA, PR number and head SHA, issuance/expiry times, unique event or attestation ID, and the intended audience/action. The verifier must own the allowlist of trusted issuer identities and algorithms; untrusted payload fields cannot choose an arbitrary trust root or downgrade the required algorithm.

Key policy should define:

1. **Validity interval:** whether the key was authorized at issuance and remains acceptable under the explicit historical-evidence policy at decision time.
2. **Revocation / compromise:** whether revocation is retroactive, which timestamp evidence is trusted, and how the verifier behaves when it cannot obtain sufficiently fresh revocation state.
3. **Rotation:** how a new key is authorized and how the previous key's acceptance window is closed. A key ID alone is not a trust anchor.
4. **Replay:** uniqueness scope for evidence IDs, acceptable re-use across independent decisions, and binding to repository, candidate, workflow, and action.
5. **Clock policy:** tolerated skew and expiry semantics, with a trusted source for current time where the decision risk requires it.
6. **Policy epoch:** the trust-policy version or epoch under which the attestation was accepted, so a policy change forces re-evaluation rather than inheriting stale eligibility.

Historical validity and present admissibility are different questions. For forensic recordkeeping, preserving that an attestation was valid under policy epoch (p_0) may be correct. For a new promotion action, policy epoch (p_1) and the current PR head govern admissibility.

## 4. Canonicalization and signature boundaries

Cryptographic signing must operate on a precisely defined byte representation. Re-serializing an equivalent-looking JSON object is not a cryptographic specification. Choose and implement one established canonicalization/signature envelope, strictly validate before acting, and domain-separate the signed purpose (for example, distinguish a CI evidence envelope from a release authorization).

[RFC 8785 — JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html) describes deterministic JSON representation for hashing/signing. It is an informational RFC, not a complete provenance system. Canonicalization solves representation ambiguity; it does not establish issuer authority, bind the CI run to the actual checked-out code, provide revocation, or prove the semantic truth of evidence.

Do not invent a bespoke signing format or claim cryptographic assurance from a test fixture. Prefer mature, documented signing/attestation infrastructure and an independently maintained verifier. Key custody, identity policy, and API collection remain part of the trusted computing base.

## 5. Threat-model matrix

| Threat | Why a naive gate fails | Required control |
|---|---|---|
| Attestation signed by an unauthorized key | Signature checks integrity, not authorization | Verifier-owned trust roots and issuer/workflow identity policy |
| Key revoked after issuance | A once-valid signature can still verify mathematically | Revocation-aware decision policy and explicit historical-validity semantics |
| Key rotation or policy change | Stale trust assumptions survive indefinitely | Policy epoch, bounded key validity, re-evaluation at action time |
| Payload re-used for a different PR or action | Authentic bytes can be replayed out of context | Audience/action binding, unique ID, exact repository/PR/SHA binding |
| Ambiguous JSON serialization | Signer and verifier may sign/check different byte sequences | Strict parse, duplicate-key rejection, defined canonicalization |
| Stale successful CI for an old head | A past successful run does not validate a new head | Re-fetch PR head and require exact SHA at the promotion boundary |
| Collector compromised or fields fabricated | Well-formed evidence may be a well-formed lie | Trusted authenticated collector, least privilege, auditable acquisition and provenance |
| Revocation service unavailable | Verifier cannot establish current key acceptability | Fail-closed for mandatory checks or a narrow, policy-approved bounded fallback |

## 6. Test / verify / run plan

These are acceptance tests to implement before changing the executable gate; they are **not asserted to have run** as a result of this document.

- **Positive:** a correctly signed envelope from an authorized issuer, bound to the current PR/repository/SHA, within the acceptance window, under current non-revoked policy is accepted for review.
- **Signature mutation:** changing any signed field without re-signing is rejected.
- **Wrong trust root / issuer / workflow identity:** rejected even when the signature is mathematically valid under some other key.
- **Revocation:** a key revoked under the configured policy cannot authorize a new promotion; the exact treatment of historically valid evidence is covered by separate explicit tests.
- **Expiry / future issuance / excessive clock skew:** rejected according to the pinned clock policy.
- **Replay:** repeated event IDs or an envelope scoped to a different audience, PR, repository, workflow, action, or commit are rejected.
- **Canonicalization ambiguity:** duplicate JSON properties, unsupported values, malformed signatures, and alternate ambiguous representations are rejected before action.
- **Policy epoch change:** evidence accepted under an obsolete policy is re-evaluated and cannot silently inherit current eligibility.
- **Unavailable trust state:** mandatory revocation or identity checks fail closed.
- **TOCTOU:** after review eligibility is computed, changing the PR head causes the downstream action-time check to stop.

Verification must include adversarial tests against the exact committed SHA, then an authenticated CI run whose job/step records and receipts are actually available. Source inspection and local reference tests must be reported separately from hosted execution.

## 7. Great Scale mapping

| Level | Mathematics | Science | Status |
|---|---|---|---|
| 5301–5310 | Evidence admissibility is a conjunction of structural, cryptographic, identity, binding, freshness, revocation, and replay predicates | Provenance requires independently trusted acquisition and context | Formal model specified |
| 5311–5320 | (A_{t_0}\not\Rightarrow A_{t_1}) in the presence of policy or state changes | CI evidence and PR state are time-dependent software facts | Deduction from the model |
| 5321–5330 | Key validity is a policy-indexed relation, not a key-ID string | Rotation and revocation are operational trust-lifecycle concerns | Requirements specified |
| 5331–5340 | Canonicalization gives an unambiguous signed representation | Stable serialization is required for reproducible signature verification | RFC 8785 referenced; implementation absent |
| 5341–5350 | Replay exclusion requires identity and context binding | Valid evidence can be misapplied outside its intended audience | Threats and controls specified |
| 5351–5360 | Fail-closed policy prevents unknown mandatory trust state from increasing eligibility | Network/API outages affect assurance decisions, not the truth of prior computations | Policy requirement, not implementation |
| 5361–5370 | Decision-time eligibility must be recomputed against current PR head and policy epoch | A green historical run is not proof of current source validity | Consistent with Levels 5101–5300 |
| 5371–5380 | Distinguish historical validity from present admissibility | Audit preservation and promotion authorization have different objectives | Semantic distinction specified |
| 5381–5390 | Acceptance properties can be framed as adversarial invariants | Security assurance needs falsification attempts and boundary tests, not only happy paths | Test plan drafted |
| 5391–5400 | A proof of structural validity cannot entail authentication without additional premises | This is software supply-chain assurance; it yields no empirical claim about quantum geometry | No code or run claimed |

## 8. Scope and conclusion

The deeper finding is a **trust-lifecycle theorem for the gate's design**: evidence eligibility is not a timeless Boolean stored inside the evidence object. It is a decision-time relation between content, identity, context, policy, revocation state, and the action being requested. The verifier must re-evaluate that relation whenever a security-relevant component can change.

This is a formalization of software-assurance requirements, not a proof that the current repository already enforces them. The existing structural gate must continue to label authentication as an external, unimplemented requirement until a trusted collector and verifier are implemented and tested. No quantum-geometric law or new physical result follows from these software-security arguments.
