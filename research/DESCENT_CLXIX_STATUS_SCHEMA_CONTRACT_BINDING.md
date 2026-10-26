# Great Scale — Descent CLXIX
## Public reachability is not contract trust

### Profound finding

The procurement evidence boundary had two separate false-positive routes:

1. `living-intermediate-control-plane/lib/evidence-console.mjs` used to label any successful HTTP response `status: "ok"` and `authority: "public"`, without parsing or validating the response body. The module also contained a TypeScript-only `export type` declaration despite its `.mjs` extension, which is not valid native JavaScript.
2. `control12-lattice-ops/procurement/evaluate.mjs` searched a merged status/schema object recursively. A live status claim missing from one document could be "satisfied" by a matching key in the other document. The prior test used the same trust fixture for both inputs, so it did not detect the source-binding failure.

These defects connect to CLXI (fallback cannot silently gain authority) and CLXII–CLXVIII (the verification path itself requires verification). Availability, contract conformance, evidence provenance, and authorization are separate propositions.

### Mathematical model

Let:
- (H): the configured public endpoint is HTTPS;
- (S): the live status document contains every required v5.3.1 trust field;
- (J): the supplied JSON Schema independently requires and constrains those fields;
- (G): exactly seven gates are present and every gate is READY;
- (R): core readiness is satisfied;
- (D): a degraded local-fallback state has actually been observed;
- (L): local-evidence opt-in is explicit;
- (F): a force-procurement request is set.

Public contract verification is:

[
P = H land S land J land G
]

The authorization rule is:

[
oxed{A = R land ig(P lor (D land L)ig)}
]

and:

[
oxed{A(F=0)=A(F=1)}
]

when every other input remains fixed. Force is not an authority input.

The source-binding invariant is:

[
oxed{S_k 	ext{ must be proven by the status document; } J_k 	ext{ by its schema}}
]

A claim in one document cannot fill a missing claim or weakened constraint in the other.

### Engineering mitigation linked across repositories

- **Living Intermediate Control Plane:** PR [#29](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/29) adds HTTPS enforcement, independent status/schema validation, exact gate checks, explicit trust-contract state, local fallback opt-in, and removes the force bypass.
- **CONTROL12 lattice operations:** PR [#31](https://github.com/doitupsolutions810-crow/control12-lattice-ops/pull/31) binds each trust claim to its source document, adds schema constraint checks, and adds preflight test wiring.
- **Great Scale:** this descent adds the CLXIX test to the aggregate command so the source-binding and authority invariants remain visible in the research acceptance suite.

### Verification

The CLXIX Python model covers valid paired documents, split-source claims, weakened schema, generic HTTP-200 bodies, a held gate, non-HTTPS public endpoints, force invariance, and explicit local fallback. It is a specification-level regression model, not a substitute for executing the JavaScript production implementation.

The focused isolated Node harness for the proposed control-plane helper/probe passed **13/13 selected tests**. A separately reconstructed focused harness for the CONTROL12 evaluator passed **6/6 selected tests**. Full repository suites were not run in this isolated session.

Hosted CI is currently unverified: the latest control-plane run reported `runner_id=0` and `steps=[]` and failed within seconds, so no test step executed. CONTROL12 lattice-ops Actions runs reported `startup_failure`. These results indicate runner/startup failure, not proof of a source-test failure or success. The deployment check is also blocked by the Vercel daily deployment-rate limit.

### Limit of the result

The v5.3.1 status/schema check establishes conformance to a declared trust contract, not cryptographic provenance of every future production artifact, signer identity, capability revocation, or an immutable execution receipt. Those remain independent Great Scale gates; no production deployment, procurement action, or PR merge is certified by this research model.
