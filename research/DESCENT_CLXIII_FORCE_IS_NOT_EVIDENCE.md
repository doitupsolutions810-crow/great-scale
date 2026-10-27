# Great Scale — Descent CLXIII: Force is not evidence

## Finding

Live source inspection of `living-intermediate-control-plane/main` shows that local-evidence opt-in is now isolated in `lib/evidence-authorization.mjs`: it returns true only for `ACCEPT_LOCAL_EVIDENCE=1`, `ACCEPT_LOCAL_EVIDENCE=true`, or `config.acceptLocalEvidenceByDefault === true`. The entry point calls this helper independently of the evidence-console probe. This is a meaningful correction to the earlier implicit-fallback finding.

A deeper authorization bypass remains in the same decision expression in `integrate.mjs`:

```js
const force = process.env.FORCE_PROCUREMENT === '1';
// ...
} else if (coreReady && (localEvidenceAuthority || force)) {
  decision = 'READY_FOR_PROCUREMENT';
}
```

This means `FORCE_PROCUREMENT=1` can make a core-ready state enter `READY_FOR_PROCUREMENT` even when public evidence has not been verified and local evidence has not been explicitly authorized. There is a second asymmetry: the decision predicate does not consult `evidenceConsole.status` / `evidenceConsole.authority` at all, so a healthy public evidence-console result does not itself authorize procurement. The variable is an override of the evidence gate, not merely a request to run an operation, while the positive public-evidence path is absent from the gate. This is a source-level control-flow finding; no exploit or production invocation is claimed.

## Formal model

Let (C) be core readiness, (P) verified public evidence, (L) explicit local-evidence opt-in, and (F) the force flag.

The observed predicate is:

[
A_{observed}=C\land(L\lor F)
]

This predicate does not require (P), and (F=1) bypasses (L). The policy should instead be:

[
\boxed{A_{safe}=C\land(P\lor L)}
]

If a force mechanism is operationally necessary, model it as a request or escalation signal, not as evidence:

[
F\not\Rightarrow P,\qquad F\not\Rightarrow L
]

## Regression integration

`test_great_scale_clxiii_force_evidence_separation.py` encodes the safe decision predicate and includes the counterexample `C=1,P=0,L=0,F=1`. It is added to the `npm run all` aggregate. This test verifies the formal policy model; it does not execute the control plane's JavaScript source. The source-level correction remains outstanding until the control-plane decision branch and its real Node self-tests are changed and run.

## Cross-repository Great Scale mapping

- **Great Scale:** keep the policy invariant executable and regression-tested.
- **Living Intermediate Control Plane:** remove `|| force` from the evidence authorization predicate; if force is retained, route it to a separate audited approval path.
- **Capability Authority:** require verified provenance for claims that a check passed; a caller-supplied override must not stand in for evidence.
- **CycleKernal:** distinguish retry/override intent from a durable authorization decision, and bind consequential writes to an idempotent operation identity.

These are architectural analogies, not a claim that the identical `FORCE_PROCUREMENT` defect exists in all four repositories.

## Verification boundary

Source evidence: `integrate.mjs`, `lib/evidence-authorization.mjs`, and `test/self-test.mjs` were fetched from the live `main` branch during this descent. The current helper and self-test support explicit local opt-in. The force bypass is visible in the entry-point condition.

The isolated policy regression is intended for local execution. No clean checkout, full `npm run all`, hosted Actions run, or live procurement invocation was performed in this pass. PR #128 remains open, draft, and unmerged; its head SHA was not available in the compact metadata response and must be re-fetched before treating any test evidence as revision-bound.
