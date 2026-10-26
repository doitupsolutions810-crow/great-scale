# Descent CLXIV — Force Is Not Evidence

## Source-level finding

Review of `living-intermediate-control-plane/integrate.mjs` at the current main branch found that the procurement decision used:

```js
coreReady && (localEvidenceAuthority || force)
```

with `force = process.env.FORCE_PROCUREMENT === '1'`. This permits the force flag to satisfy the evidence side of the gate. The inverse mismatch also existed: the variable named `localEvidenceAuthority` represented only explicit local opt-in, so a healthy public evidence-console response did not independently satisfy that condition.

This is a source-level policy flaw, not evidence of an exploited or deployed incident.

## Corrected invariant

Let:
- (C) = core readiness passes.
- (P) = evidence console status is `ok` and authority is `public`.
- (U) = explicit local-evidence opt-in.
- (F) = force flag is set.

The unsafe gate was (C land (U lor F)), which treats (F) as evidence.
The intended gate is:

[
oxed{A = C land (P lor U)}
]

and therefore:

[
rac{partial A}{partial F}=0
]

in the logical sense that changing (F) alone cannot change authorization. Force may express operational intent; it must not manufacture provenance or trust.

## Integration

A source-level correction is proposed in [Living Intermediate Control Plane PR #28](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/28):
- dedicated `lib/procurement-evidence-policy.mjs` helper;
- verified public success or explicit local opt-in is required;
- the `FORCE_PROCUREMENT` bypass is removed from the evidence gate;
- self-tests cover public success, degraded local fallback, explicit opt-in, and unknown authority.

The PR is open, draft, and unmerged. No production deployment claim is made.

## Great Scale regression

`test_great_scale_clxiv_evidence_authorization_independence.py` adds a truth-table model and is included in `npm run all`. It checks that force cannot bypass missing/unknown evidence and that core readiness remains necessary.

## Verification status

- Isolated JavaScript policy harness: 6/6 cases passed, exit code 0. This exercised a local copy of the helper logic, not the complete repository checkout.
- Great Scale CLXIV model test: will be run separately before reporting a result.
- Control-plane full `npm test`, end-to-end dry-run, and hosted CI: not yet verified.
- Great Scale full aggregate and hosted Actions for the exact current branch head: not verified.

## Great Scale principle

[
oxed{	ext{Operational Override} 
e 	ext{Evidence Authorization}}
]

Every override must be scoped to a decision dimension; it cannot silently waive independent safety predicates.
