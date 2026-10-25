# Descent XCIX — Four Independent Proof Obligations

## Finding

A digest, signature reference, successful test, or green-looking status string is not a complete proof of a trusted operation. Four propositions must be kept separate:

- **Integrity (I):** the bytes/witness match the claimed digest.
- **Authenticity (A):** the producer is verified against a trusted identity.
- **Execution (E):** the claimed command actually ran on the intended revision and environment, with an observed result.
- **Authority (P):** the current principal is authenticated and authorized for this action on this resource.

The strict acceptance rule is:

\[
\operatorname{Accept}(W,q) = I(W) \land A(W) \land E(W) \land P(q,W)
\]

No predicate implies the others. A correct digest can describe malicious content; a valid signature can attest to an unexecuted command; an executed test can be tied to the wrong revision; and a fully valid artifact does not authorize a caller to access another user's data.

## Mathematical model

Let the evidence object be \(W=(b,h,s,c,r)\), where \(b\) is the payload, \(h\) its digest, \(s\) signature/attestation, \(c\) command plus exit code, and \(r\) the tested revision. Let \(q\) be the caller and requested resource.

\[
I(W)=[H(b)=h]
\]
\[
A(W)=\operatorname{Verify}(s,h\parallel r\parallel c,K_{trusted})
\]
\[
E(W)=\operatorname{ObservedRunnerExecution}(r,c,\operatorname{exit}=0)
\]
\[
P(q,W)=\operatorname{Authenticated}(q)\land\operatorname{Authorized}(q,\operatorname{action},\operatorname{resource})
\]

This model binds the attestation to repository, revision, workflow, command, environment, outcome, and artifact identity. Signing only a payload digest does not establish that a specific test ran or that the current caller is authorized.

## State-space result

There are \(2^4=16\) Boolean states. Exactly one satisfies strict acceptance: \((I,A,E,P)=(1,1,1,1)\). The executable test enumerates every state and checks that removing any one gate rejects the request.

The test validates the logical contract only. It is not a cryptographic implementation, production authorization test, or proof that a hosted runner executed.

## Practical mapping

- **Great Scale:** a content fingerprint can prove witness consistency, not the identity of the supplier or execution of a computation.
- **CycleKernal:** the inspected backend accepts request-supplied `userId` and `universeId` on data routes without showing principal/resource binding in that file. A separate effect/evidence failure window exists on chat saves: MongoDB persistence occurs before later operations and the HTTP response.
- **Capability Authority:** a signed receipt must bind the structured action, issuer, policy context, and evidence identity; signature validity alone does not prove policy admission or durable recording.
- **Living Intermediate Control Plane:** structural validation cannot replace signature verification, trusted issuer checks, revocation checks, or runner evidence.
- **GitHub Actions:** a failed job with no runner allocation or executed steps is execution-unverified, not proof that tests ran and failed, and not a pass.

## Acceptance and operational protocol

1. Hash canonical payload bytes and compare with the claimed digest.
2. Verify the signature/attestation under an explicitly trusted identity.
3. Bind evidence to repository, exact commit SHA, workflow identity, command, environment/image digest, exit code, and artifact digest.
4. Require observed execution with exit code zero and all required test/build steps present.
5. Authenticate the caller server-side; authorize each action and target resource. Never treat request-supplied identifiers as proof of ownership.
6. Treat missing logs, runner allocation, step records, artifact provenance, or authorization context as **unverified/denied**, not successful.
7. Keep effect status, evidence durability, and caller acknowledgement distinct. A failed acknowledgement does not prove that no write occurred.
8. Do not let a checksum, status badge, signature, or test report substitute for the other proof layers.

## Concrete counterexamples

### Authenticity collapse

The Living Intermediate Control Plane session-link verifier previously computed:

`ok = digestOk && (signatureOk === null ? true : signatureOk === true)`

When no HMAC trust key was configured, a digest-consistent unsigned record could return `ok: true`. That established integrity, not authenticity. The correction is tracked in [LICP PR #24](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/24); the change remains open/unmerged and the prior hosted run lacked usable step logs.

### Authorization collapse

CycleKernal's default-branch `backend/server.js` at blob SHA `fa16b63e56213fb031624c01b124db900adcb0c3` accepts `userId` / `universeId` from request parameters or bodies on chat and snapshot routes, while the inspected file does not show authenticated-principal binding. The dashboard, active-user count, and metrics endpoints also lack route-level auth checks in that file. This is source-level evidence only; deployment reachability and upstream controls were not verified.

### Acknowledgement/effect collapse

CycleKernal's `POST /api/chat/save` saves a MongoDB record before running `countDocuments`, writing Redis, and returning success. If a later step fails, the handler can return HTTP 500 even though the MongoDB write already succeeded. A retry may create a duplicate because the route shows no idempotency key or uniqueness contract. The snapshot route has a similar ambiguity if persistence succeeds but the response is lost. See [Great Scale PR #127](https://github.com/doitupsolutions810-crow/great-scale/pull/127) for the state model.

## Scope and limitations

This is an engineering model, not a physical law. The finite-state test checks only the acceptance rule. No cryptographic verifier, live runner, deployed service, or real database failure was exercised by this note. Repository-level enforcement still requires implementation and negative integration tests.
