# Great Scale — Descent CLXIX
## Public reachability is not contract trust

### Profound finding

The procurement evidence boundary had multiple independent false-positive routes:

1. `living-intermediate-control-plane/lib/evidence-console.mjs` previously treated any successful HTTP response as public authority without validating its body. It also contained a TypeScript-only `export type` declaration inside a `.mjs` module, which is invalid native JavaScript.
2. `control12-lattice-ops/procurement/evaluate.mjs` previously searched a merged status/schema object recursively. A live status claim missing from one document could be "satisfied" by a matching key in the other document.
3. The evidence fetchers followed redirects. A configured HTTPS URL could therefore return data from another final URL, while the caller treated that response as evidence from the configured endpoint.
4. Seven READY statuses are not enough if an ID is duplicated, missing, or replaced by an unknown gate.

These defects connect to CLXI (fallback cannot silently gain authority) and CLXII–CLXVIII (the verification path itself requires verification). Availability, contract conformance, endpoint identity, freshness, provenance, and authorization are distinct obligations.

### Mathematical model

Let:

- (H): the configured public endpoint uses HTTPS.
- (E): the response remains bound to the exact requested HTTPS URL; redirects are refused.
- (S): the live status document contains every required v5.3.1 trust field.
- (J): the JSON Schema independently requires and constrains those fields.
- (G): the exact set `G0`–`G6` appears once, and every status is READY.
- (R): core readiness is satisfied.
- (D): a degraded local-fallback state has actually been observed.
- (L): local-evidence opt-in is explicit.
- (F): a force-procurement request is set.

The public contract predicate is:

```text
P = H ∧ E ∧ S ∧ J ∧ G
```

The authorization rule is:

```text
A = R ∧ (P ∨ (D ∧ L))
```

Force must not change authorization when every other input is fixed:

```text
A(F=0) = A(F=1)
```

Source binding is another independent condition: `S_k` must be proven by the live status document, while `J_k` must be proven by the schema. A claim in one document cannot fill a missing claim or weakened constraint in the other.

For array-form gates, the schema must constrain each item’s `id` to G0–G6 and `status` to READY, require exactly seven items, and include a `contains` constraint with `minContains: 1` and `maxContains: 1` for each ID. For object-form gate maps, all seven keys must be required and each value must be constrained to READY.

### Engineering mitigation linked across repositories

- **Living Intermediate Control Plane:** [PR #29](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/29) makes procurement authorization explicit, removes the force bypass, validates status and schema independently, requires exact gate coverage, refuses redirects, and disables client-side HTTP caching for the trust fetch.
- **CONTROL12 lattice operations:** [PR #31](https://github.com/doitupsolutions810-crow/control12-lattice-ops/pull/31) binds trust claims to their source document, validates object/array gate shapes, pins evidence fetches to HTTPS endpoints, and adds regression tests and preflight wiring.
- **Great Scale:** this descent adds CLXIX to `npm run all` and records the formal authority contract and verification limits.

### Verification

The CLXIX Python model covers 14 cases: valid paired documents, split-source claims, weakened schema, generic HTTP-200 bodies, a held gate, non-HTTPS endpoints, force invariance, explicit local fallback, missing gate requirements, unknown gate IDs, valid array-form exact-once gate coverage, a weakened array schema, a cross-origin final response URL, and an object-form schema that attempts to permit extra gate IDs.

Reconstructed focused local harnesses passed:
- **19/19** Node authorization/probe tests, including redirects, cache directives, exact gate identity, and source binding.
- **14/14** CONTROL12 evaluator tests, including object- and array-form schemas and pinned HTTPS fetching.
- **14/14** CLXIX model tests.

These were isolated, locally reconstructed harnesses. They are not a full clean-checkout execution of the committed repository suites. Native access to the GitHub checkout was unavailable in the local execution environment.

Hosted CI remains unverified. Latest observed Actions runs: control-plane [40423428848](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/actions/runs/40423428848) and Great Scale [40423478954](https://github.com/doitupsolutions810-crow/great-scale/actions/runs/40423478954) report `runner_id=0` and zero steps; CONTROL12 [40423464960](https://github.com/doitupsolutions810-crow/control12-lattice-ops/actions/runs/40423464960) returned `startup_failure` with no job records. No test step ran, so these results demonstrate neither a code test failure nor a pass. Vercel deployment checks remain blocked by the account deployment-rate limit. Snyk/CodeRabbit success does not replace CI.

### Remaining acceptance gap: freshness and cryptographic provenance

The v5.3.1 contract validator checks the declared fields and schema shape but does not validate a signed status statement, signer identity, immutable receipt, sequence/checkpoint, or a source-generated `generatedAt`/expiry field. The fetcher requests `no-store` and `no-cache`, which reduces client-side reuse, but does not prove that the remote service itself produced a fresh response. **Freshness and cryptographic provenance remain unproven acceptance gates.** They must not be inferred from HTTPS, contract conformance, or endpoint reachability.

No production deployment, procurement action, PR merge, or end-to-end production behavior is certified by CLXIX.
