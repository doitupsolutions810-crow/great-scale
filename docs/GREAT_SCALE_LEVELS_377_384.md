# Great Scale — Levels 377–384: Identity Is Provenance, Not Input

**Status:** source-level data-flow finding plus proposed security invariant. Reviewed source: TrainLLM `full_cyclekernel_buildA_FH_complete.py`. Related findings: [issue #5 — bind chat-memory identity to authenticated principal](https://github.com/doitupsolutions810-crow/TrainLLM/issues/5) and [issue #2 — truncated user IDs](https://github.com/doitupsolutions810-crow/TrainLLM/issues/2). This is an application-security mapping, not a physical claim.

## Level 377 — Trace the identity dataflow

The `/chat` handler reads `user_id` from request JSON, falling back to `default_user`, and passes that value to both `get_context_from_memory(user_id)` and `process_interaction(user_id, ...)`. The bridge indexes memory by this value. The reviewed file shows no route-level authentication check before the memory read/write. Broad CORS and Socket.IO origin configuration are also present, but CORS is not an authorization mechanism.

The security conclusion is conditional: if no trusted authentication boundary exists upstream and the service is reachable by untrusted callers, request-supplied identity is not sufficient to establish memory ownership. Deployment middleware and live reachability were not inspected.

## Level 378 — Separate asserted identity from authenticated principal

Let (u_e) be the identity string asserted inside event (e), (p_e) the principal established by a trusted authentication boundary, and (owner(r)) the owner of memory resource (r).

**Definition:** (u_e) is untrusted event data. (p_e) is verified identity context. They are not interchangeable.

A valid access predicate is:

\[
\operatorname{Permit}(e,r,a)=\operatorname{Authenticated}(p_e)\land\operatorname{Authorize}(p_e,r,a).
\]

The event's own claimed identity must not be an input that can independently make this predicate true.

## Level 379 — Ownership invariant

For every memory read or write:

\[
\operatorname{MemoryAccess}(e,r)\Rightarrow
\operatorname{Authenticated}(p_e)\land
\big(\operatorname{Owner}(r)=p_e\;\lor\;\operatorname{ExplicitGrant}(p_e,r)\big).
\]

A string equality `request.user_id == memory.user_id` is not proof of ownership when both strings are caller-controlled.

## Level 380 — Cross-boundary composition

The approval and memory findings compose. A system can have a perfectly deterministic state transition and still be unsafe if the identity authorizing it is spoofable. Conversely, a valid principal is not enough if confidence scores can approve changes without authorization.

Required composite guard:

\[
\operatorname{Apply}(q,e)\Rightarrow
\operatorname{AuthorizedPrincipal}(e)\land
\operatorname{ScopedApproval}(q,e)\land
\operatorname{HashMatch}(q)\land
\operatorname{Fresh}(e).
\]

Identity, authority, content binding, and freshness are independent gates; none should be collapsed into a single trust score.

## Level 381 — Internal IDs and external identities

The six-character ID truncation tracked in issue #2 is a separate failure mode. A safer design uses an opaque, collision-resistant internal key and a server-controlled mapping from authenticated subject to internal record. Do not use a short prefix of a user identifier as the primary key, and do not let the client choose the internal key.

## Level 382 — Deterministic security regressions

Required tests before promotion; these are test specifications, not executed tests:

1. No authenticated principal ⇒ memory read and write denied.
2. Request asserts another user's ID ⇒ the assertion is ignored or rejected; no cross-user access.
3. Authenticated user A requests user B's memory ⇒ denied without an explicit grant.
4. Missing `user_id` never maps unrelated callers to a shared `default_user`.
5. Two distinct authenticated subjects sharing the same six-character prefix remain distinct.
6. WebSocket events containing per-user state are delivered only to authorized sessions, not broadcast to all clients.
7. A valid identity with an invalid approval signature still cannot apply a proposal.
8. A valid approval from the wrong principal or scope is rejected.

## Level 383 — Receipt and replay contract

For every access or mutation, record an integrity-protected receipt containing a pseudonymous principal identifier, resource key, action, policy version, decision, timestamp/sequence, and resulting state revision. Avoid logging raw secrets or unnecessary personal data. Replay must reproduce the decision from the same authenticated context and policy revision; a client-supplied identity field is never the replay authority.

## Level 384 — Falsification gate

**Falsifier:** an unauthenticated or differently authenticated request can read or mutate another principal's memory solely by changing its JSON `user_id`. Any reproducible trace of this kind violates the ownership invariant.

**Verification status:** source-level dataflow supports the risk hypothesis; external middleware, deployment topology, live exploitability, and repository tests have not been verified. The appropriate next step is authenticated identity binding plus deterministic cross-tenant tests, not a speculative live attack.