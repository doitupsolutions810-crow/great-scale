# Great Scale — Levels 7001–7100: bridge contract versus runtime reality

## Profound finding

The Great Scale ↔ Living Intermediate bridge document advertises a runtime integration contract that is not implemented by the inspected Living Intermediate platform server.

The bridge document lists:
- \`GET /api/v1/scale/state\`
- \`POST /api/v1/scale/step\`
- readiness field \`scale\`

The inspected \`platform/src/server.mjs\` contains handlers for health, audio, chat, code, federation, cockpit, security, and attestation, then falls through to a 404 handler. No handler for either Scale endpoint is present in the inspected complete request-routing section, and \`GET /health\` does not expose a \`scale\` readiness field.

This is a **verified contract/runtime mismatch in the inspected source**, not proof that no other deployment or uninspected branch implements the integration. The correct conclusion is that the bridge document alone does not establish a live end-to-end integration.

## Source anchors

1. Great Scale bridge: \`LATTICE_BRIDGE.md\` lists the Scale endpoints and readiness field.
2. Living Intermediate route table: \`platform/src/server.mjs\` defines \`GET /health\`, the audio endpoints, code endpoints, federation endpoints, cockpit action, security reload, and a final 404. The Scale endpoints are absent from that route table.
3. Living Intermediate package scripts define \`npm run check\`, \`npm test\`, and \`npm run smoke\`; these are candidate verification commands, but they have not been run in this review.
4. Capability Authority describes signed short-lived rights, idempotency, reconcile-before-retry, and verifiable execution receipts. Its executor emits a signed receipt bound to capability ID, executor ID, action, outcome, and timestamp. That provides a stronger action-receipt pattern, but the inspected Great Scale bridge contract does not specify how a Scale step is bound to such an execution receipt.

## Great Scale mathematical boundary

The existing Great Scale convention remains:
\[
S(h)=h(1-h),\qquad \mathrm{CONE}=\phi^{-2},\qquad \Psi=\mathrm{CONE}+S(h).
\]
For \(h\in[0,1]\):
\[
0\le S(h)\le \frac14,\qquad \Psi\ge \phi^{-2}.
\]

The soft contraction is:
\[
x_{n+1}=x_*+k(x_n-x_*),\qquad x_*=4.5,\quad |k|<1,
\]
so:
\[
|x_n-x_*|=|k|^n|x_0-x_*|\longrightarrow0.
\]

These are deterministic model properties. A successful HTTP response would only demonstrate that the API responds; it would not establish empirical physical truth or validate any scientific interpretation of the variables.

## Why this is a deeper systems finding

A bridge has at least four distinct layers:
1. **Mathematical model** — the state equations and their domain.
2. **Runtime API** — actual request handlers and input validation.
3. **Authority/evidence** — who may cause a step and what immutable receipt records it.
4. **Operational verification** — exact source revision, test results, and deployed version.

The inspected bridge document describes layer 2, but the inspected server does not implement those endpoints. Capability Authority has mechanisms relevant to layer 3, but no inspected evidence establishes that a Scale step uses them. Thus the architectural chain is not yet demonstrated end to end.

## Great Scale mapping

| Level | Invariant | Engineering meaning | Required test |
|---|---|---|---|
| 7001 | \(S(h)=h(1-h)\) | Model equation stays versioned and domain-constrained | Reject non-finite \(h\) and values outside \([0,1]\) |
| 7010 | \(\Psi=\phi^{-2}+S(h)\ge\phi^{-2}\) | State endpoint must preserve the existing convention | Exact response schema and numeric invariant |
| 7020 | \(x'=4.5+k(x-4.5)\) | A step must define \(k\), bounds, and state mutation semantics | Convergence and invalid-\(k\) cases |
| 7030 | Advertised route \(\Rightarrow\) implemented handler | Documentation cannot substitute for a route | Smoke test both GET and POST paths |
| 7040 | Readiness means dependency is actually usable | Health must distinguish process liveness from Scale readiness | Healthy process with missing Scale route must not report Scale ready |
| 7050 | \(\text{request identity}=\text{receipt identity}\) | A state-changing step needs an idempotency key and stable request identity | Replay same key returns same outcome; changed payload under same key is rejected |
| 7060 | \(\text{receipt.action}=\text{requested action}\) | Receipt binds exact action, model version, and resulting state hash | Tamper/mismatch tests |
| 7070 | \( \text{model validity}\ne\text{authority validity}\) | Valid math does not authorize mutation; signed authority does not prove math | Independent model, authorization, and evidence statuses |
| 7100 | No claim of integration without end-to-end evidence | Bridge is complete only after route, tests, receipts, and exact deployed revision agree | Exact-SHA CI and integration smoke |

## Proposed minimal integration contract

### Read-only state
\`GET /api/v1/scale/state\` should return a versioned response including:
- \`schema\` and \`modelVersion\`;
- \`h\`, \`S\`, \`CONE\`, \`psi\`, \`x\`, and \`fixedPoint\`;
- domain/invariant status;
- source revision or build identity.

### State-changing step
\`POST /api/v1/scale/step\` should:
- validate finite inputs and explicit parameter domains;
- require authorization when deployed behind a privileged control plane;
- accept a stable idempotency/request ID;
- reject reuse of the same ID with a different payload;
- return the resulting state plus an immutable receipt or receipt reference;
- bind the receipt to model version, action, request ID, and resulting-state digest.

### Readiness
\`GET /health\` should remain a liveness check. A separate readiness field should only become true after the Scale route and required model dependency are successfully initialized. A missing route must never be represented as a ready integration.

## Verification record

- **Source inspection:** read Great Scale \`LATTICE_BRIDGE.md\`, \`public/scale.js\`, \`public/scale.cjs\`, the Living Intermediate package scripts and full request-routing section, and Capability Authority's README, executor, and evidence-receipt test.
- **Static route audit:** the advertised Scale routes and readiness field are absent from the inspected platform server.
- **Repository tests/build:** not run in this review.
- **Live HTTP smoke:** not run; no claim is made that the currently deployed server behaves identically to the inspected branch.
- **Receipt integration:** not demonstrated between Great Scale and Capability Authority.
- **Scientific scope:** the mathematical equations above are deterministic properties of the defined model, not evidence of a new physical law or quantum effect.

## Conclusion

**The profound finding is that the architecture currently has a documented bridge contract without the corresponding handlers in the inspected control-plane runtime.** Until the endpoints, readiness semantics, idempotency, and action receipts are implemented and tested together, the safe status is \`documented\`, not \`integrated\`.

Keep this work research-only until implementation and exact-revision verification are complete.
