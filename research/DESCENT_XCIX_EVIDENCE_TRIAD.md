# Descent XCIX — Integrity, Authenticity, and Execution Are Independent

## Finding

A digest, signature reference, or green-looking status string is not a complete proof of a successful trusted operation. Three independent propositions must be distinguished:

- **Integrity (I):** the received bytes/witness match the claimed digest.
- **Authenticity (A):** the producer is the expected identity and the signature/attestation verifies under a trusted key or trust root.
- **Execution (E):** the claimed command actually ran on the intended revision/environment and its result was observed.

A complete acceptance decision requires all three:

\[
\mathrm{Accept} \Rightarrow I \land A \land E
\]

No one of these propositions implies either of the others. A correct digest can describe malicious content; a valid signature can sign a claim about a command that never ran; an executed test can be unauthenticated or associated with the wrong commit.

## Mathematical model

Let the evidence object be \(W=(b,h,s,c,r)\), where \(b\) is the payload, \(h\) its digest, \(s\) signature/attestation, \(c\) command plus exit code, and \(r\) the tested revision.

Define:
\[
I(W)=[H(b)=h]
\]
\[
A(W)=\mathrm{Verify}(s, h \parallel r \parallel c, K_{trusted})
\]
\[
E(W)=\mathrm{ObservedRunnerExecution}(r,c,exit=0)
\]

Then:
\[
\mathrm{Accept}(W)=I(W)\land A(W)\land E(W)
\]

This model deliberately binds the signature to the revision, command, and outcome. Signing only the payload digest leaves room for a validly signed artifact to be misrepresented as having passed a particular test.

## Practical mapping to the repositories

- **Great Scale:** a content fingerprint can prove that a witness matches an identifier, but not who supplied it or whether a computation ran.
- **CycleKernal:** fusion_state_id / canonical witness consistency protects internal integrity; the repository explicitly notes that this does not authenticate the upstream relay.
- **Capability Authority:** a signed receipt must bind the structured action, issuer identity, policy context, and evidence identity; signature validity alone does not prove policy admission.
- **Living Intermediate Control Plane:** a structural acceptance validator can reject incomplete metadata, but cannot replace cryptographic signature verification, trusted issuer checks, revocation checks, or real runner evidence.
- **GitHub Actions:** a failed job with runner ID 0 and no executed steps is execution-unverified, not a test failure and not a pass.

## Executable contract test

test_evidence_triad.py exhaustively enumerates the 8 Boolean combinations of integrity, authenticity, and execution. Acceptance is true in exactly one state: all three are true. This checks the acceptance rule; it is not a cryptographic implementation or proof that any specific CI runner executed.

## Acceptance protocol

1. Hash canonical payload bytes and compare to the claimed digest.
2. Verify a signature/attestation under an explicitly trusted identity.
3. Bind the attestation to repository, exact commit SHA, workflow identity, command, environment/image digest, exit code, and artifact digest.
4. Require independently observed execution with exit code zero and all required test/build steps present.
5. Treat missing logs, missing runner allocation, missing step records, or missing artifact provenance as **unverified**.
6. Do not let a checksum, status badge, signature, or test report substitute for the other proof layers.

## Scope and limitations

This is an engineering evidence model, not a physical law. The finite-state test validates only the logical acceptance rule. No cryptographic verifier, hosted runner, deployment, or external artifact was exercised by this note. Repository-specific integration must implement and test the predicates above.

## Concrete cross-repository counterexample

The Living Intermediate Control Plane session-link verifier previously computed:
`ok = digestOk && (signatureOk === null ? true : signatureOk === true)`.
When no HMAC trust key was configured, a digest-consistent unsigned record could therefore return `ok: true`. That result established integrity only; it did not establish authenticity. The verifier's module documentation says session links are evidence-only, so this finding does not imply an execution gate was bypassed. It does show that a single success boolean can collapse distinct proof obligations and mislead downstream consumers.

The follow-up fix is tracked in [Living Intermediate Control Plane PR #24](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/24). It makes `ok` require both digest integrity and authenticated HMAC verification, and returns separate `integrityOk`, `authenticated`, and `reason` fields. The change is open and unmerged; hosted CI reported failure but its job had no step records and its logs were unavailable, so the source change remains unverified by that run.

This is an example of a general anti-pattern:
[
\text{one status bit} \not\equiv \text{complete proof}
]
A safe API should expose the predicates independently, then define acceptance as their conjunction.


## Descent C — authorization is a fourth, independent proof obligation

A deeper inspection of CycleKernal's default-branch `backend/server.js` at blob SHA `fa16b63e56213fb031624c01b124db900adcb0c3` found that the inspected Express routes do not establish an authenticated principal or bind the requested resource identifier to that principal. Examples include:

- `POST /api/chat/save` accepts `userId` from the request body.
- `GET /api/chat/history/:userId` selects records using the caller-supplied path parameter.
- `POST /api/simulation/snapshot` accepts `universeId` from the request body; the read route similarly selects by the path parameter.
- `/api/analytics/dashboard`, `/api/users/active`, and `/metrics` have no route-level authentication check in this file.

This is a source-level observation, not proof that a deployed service is reachable from the public internet or that an incident occurred. Network controls, upstream middleware, and deployment configuration were not verified. The inspected file itself does not show the principal/resource binding needed to enforce per-user authorization.

### Refined acceptance equation

Integrity, evidence authenticity, observed execution, and caller authority are distinct:

- (I): payload integrity is established.
- (A): evidence issuer authenticity is established.
- (E): the claimed command actually ran and its result was observed.
- (P): the current principal is authenticated, authorized for the action, and bound to the target resource.

[
mathrm{Accept}(W, q) Rightarrow I(W) land A(W) land E(W) land P(q, W)
]

A validly signed receipt does not authorize the current caller to read another user's history. A caller-supplied `userId` is a selector, not proof of ownership. Likewise, an internal digest does not prove that a request is permitted.

This expands the earlier three-gate model to four independent Boolean proof obligations. There are (2^4=16) states; exactly one state satisfies the strict acceptance rule. Production enforcement still requires actual authentication middleware, server-derived identity, resource ownership/tenant checks, and negative integration tests. The finite-state test only checks the logical contract.
