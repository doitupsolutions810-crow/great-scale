# Descent CLXI — Availability Fallback Must Not Imply Authorization

## Cross-repository evidence

Inspected `living-intermediate-control-plane/lib/evidence-console.mjs` and `integrate.mjs` on 2026-10-26.

The probe returns `authority: 'local'` for missing, 404, non-OK, or unreachable public evidence when `acceptLocal: true`. The integration caller invokes `probeEvidenceConsole({ acceptLocal: true })`, then computes:

```js
const localEvidenceAuthority =
  process.env.ACCEPT_LOCAL_EVIDENCE === '1' ||
  process.env.ACCEPT_LOCAL_EVIDENCE === 'true' ||
  config.acceptLocalEvidenceByDefault === true ||
  (evidenceConsole.authority === 'local' && evidenceConsole.status !== 'ok');
```

The final clause independently accepts degraded local authority. Consequently, a missing or unreachable public evidence console can make `localEvidenceAuthority` true even when neither explicit environment opt-in nor configuration opt-in is set. This is not merely a theoretical state: the repository README says the URL may be unset and local authority is used, and its self-test intentionally verifies local authority on unconfigured, 404, and unreachable responses.

## Profound finding

**Availability fallback is being promoted into authorization.** The code preserves the label `authority: 'local'` in the result, but the procurement decision predicate treats that local result as sufficient. A system can therefore remain operational while silently weakening the evidence requirement.

This is a policy mismatch, not proof of exploitation or of an external attacker. It may be intentional for a lab or availability-first mode, but then the mode should be explicitly configured and unmistakably reported.

## Formal model

Let (A) be availability, (U) be explicit local-evidence opt-in, (P) be a successful public evidence check, and (R) be procurement readiness.

The observed predicate includes an implicit fallback term:

[
U = U_{env} lor U_{config} lor
(	ext{authority}=	ext{local}land	ext{status}
e	ext{ok})
]

A fail-closed authorization policy separates the two:

[
operatorname{EvidenceAccepted}
= P lor U
]

where (P=(	ext{status}=	ext{ok}land	ext{authority}=	ext{public})), and local evidence is accepted only when (U_{env}lor U_{config}) is explicitly true.

Thus:

[
	ext{FallbackAvailable}
otRightarrow	ext{EvidenceAuthorized}
]

## Regression

`test_great_scale_clxi_authority_preserving_fallback.py` reproduces the current predicate's counterexample and tests the corrected decision rule across 404, unreachable, unconfigured, invalid, public success, and unknown-authority cases. It is included in Great Scale's aggregate test manifest.

The test is a model regression; it does not import or execute the other repository's JavaScript. Source-level integration should follow by extracting a pure authorization helper in the control-plane repo and testing the real helper.

## Recommended source fix

In `living-intermediate-control-plane/integrate.mjs`, remove the implicit final clause from `localEvidenceAuthority`. Keep local fallback available for diagnostics and readiness reporting, but require `ACCEPT_LOCAL_EVIDENCE=1` or `config.acceptLocalEvidenceByDefault === true` before it authorizes procurement. Add explicit output such as `evidenceMode: 'public' | 'local-opt-in' | 'local-not-authorized'` and ensure public-console failure cannot be mistaken for public verification.

## Limits

This finding is grounded in inspected source and self-test code. The remote domain's current HTTP behavior was not freshly probed in this step. No production behavior was changed in the control-plane repository, and no full cross-repository suite was run.
