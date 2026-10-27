# Descent CLXI — Availability Fallback Must Not Imply Authorization

## Cross-repository source change

Inspected `living-intermediate-control-plane/integrate.mjs`, `lib/evidence-console.mjs`, and `test/self-test.mjs` on 2026-10-26.

The original integration accepted local fallback implicitly when `authority === 'local'` and `status !== 'ok'`. That clause has now been removed from `integrate.mjs`. The policy is isolated in `lib/evidence-authorization.mjs` as `acceptsLocalEvidence`, and the procurement decision consumes that helper.

The helper accepts local evidence only when `ACCEPT_LOCAL_EVIDENCE=1`, `ACCEPT_LOCAL_EVIDENCE=true`, or `config.acceptLocalEvidenceByDefault === true`. The default `npm run procure` and `npm run procure:gated` commands have now been changed to **not** inject `ACCEPT_LOCAL_EVIDENCE`. Explicit fallback modes are available as `npm run procure:local` and `npm run procure:gated:local`. The README operator loop documents the distinction, and the control-plane self-test checks the script definitions.

Commits on the control-plane main branch:
- helper module: `31418d7a711f0b8c4b7bd3b8449551fd42f0be3d`
- integration refactor: `aaa2a88a15d26c4cc64c46857139d89358b9a5b1`
- self-test coverage: `451eaba2d6c3dc835a861cf675e9d3e861780b0e`

## Profound finding

Availability fallback is not merely a monitoring detail: it sits on the path to procurement authorization. The former code preserved `authority: 'local'` as metadata but then treated a degraded local result as sufficient. The source change removes that implicit widening of authority.

This establishes a policy correction in source, not proof that a production deployment has already adopted the new commits.

## Formal model

Let (P) mean a successful public response, (U_e) explicit environment opt-in, and (U_c) explicit configuration opt-in.

[
operatorname{EvidenceAccepted}=Plor U_elor U_c
]

with:

[
P=(	ext{status}=	ext{ok})land(	ext{authority}=	ext{public})
]

Therefore:

[
	ext{FallbackAvailable}
otRightarrow	ext{EvidenceAuthorized}
]

## Regression

`test_great_scale_clxi_authority_preserving_fallback.py` models the corrected helper. It covers degraded local statuses, explicit opt-in, public success, and unknown/mismatched authority. The test is included in Great Scale's aggregate suite.

The control-plane self-test now directly exercises the actual JavaScript helper and asserts that the default procurement scripts do not enable local fallback. The full control-plane suite and a production deployment verification remain outstanding.

## Operational note

The explicit local mode is still available by design. Operators should treat it as a weaker, deliberate mode and ensure decision outputs make that mode visible. If local evidence is not acceptable for a particular procurement action, do not set the opt-in and require public evidence.

## Hosted CI status observed after the source fix

The latest Living Intermediate Control Plane main commit observed was `8510bff879dd4f21ae5d8f7265a49ff9a53fec57`. Its GitHub Actions run `40401004658` (Plane CI) completed with conclusion `failure`; the container job was skipped. The connected integration could retrieve job metadata but not the hosted log blob, so the cause is unknown and must not be attributed to these changes without further evidence.

For the current Great Scale research head `03266e32310bfd560b287c7fb61d7a01fc35a604`, the queried Actions endpoint returned zero runs. Therefore, the isolated tests below are not a substitute for hosted CI.

## Verification limits

The source edits, explicit-mode script split, README clarification, and self-test assertions are committed to the control-plane main branch. The complete cross-repository suites have not been run in this environment. No claim is made that hosted CI passed or that deployed behavior has changed.
