# Great Scale — Levels 8325–8336: bounded, unambiguous evidence ingress

## Finding

The proof kernel's serialized wrappers now bound and disambiguate proof inputs, but the promotion gate's CLI had a separate path: it read an evidence file in full and called `JSON.parse` directly. That path did not inherit the proof kernel's byte/depth/value limits or duplicate-key policy. A large evidence file could consume unnecessary resources, and duplicate keys could be interpreted differently by this gate and another verifier, logger, or signer.

This is a source-level boundary mismatch. No live exploitation or deployment impact has been demonstrated.

## Integration

- Added a 1 MiB evidence-file cap checked using the opened descriptor's metadata, then read at most cap+1 bytes so a concurrent file growth cannot force an unbounded read allocation; the decoded string is byte-checked again.
- Added an iterative pre-parse scanner with bounds on nesting depth, object-key count, array item count, and aggregate JSON values.
- The scanner compares decoded key strings, rejecting escaped-equivalent duplicates as well as literal duplicate names.
- The CLI now passes the bounded scanner before materializing evidence with `JSON.parse`.
- Added CLI regression cases for duplicate keys and over-limit files.
- Kept `evaluatePromotionEvidence(evidence)` as an object-level structural policy function for compatibility. Callers that bypass the CLI must enforce equivalent ingress bounds themselves; the gate still does not authenticate the collector.

## Mathematics

Let (J) be the serialized evidence and (P(J)) its parsed object. Ordinary JSON parsing can collapse distinct byte strings into the same object when duplicate keys are present. A safer ingress contract requires:

[
|J|_{\mathrm{bytes}}\le B,\qquad
\operatorname{depth}(J)\le D,\qquad
\max_o |\operatorname{keys}(o)|\le K,
]

and for every object (o),

[
i\ne j\implies k_i(o)\ne k_j(o),
]

where keys are compared after JSON string decoding. These constraints bound representation and remove one class of ambiguous interpretation. They do not prove that the evidence is truthful or that its claimed tests ran.

## Science and engineering interpretation

The important invariant is **assurance-path parity**: the policy engine should not accept serialized evidence through a weaker representation boundary than the proof kernel uses for claims. More generally, a security claim applies only to the entry points that actually enforce it.

This is a software assurance result, not a new physical law or empirical confirmation of quantum geometry.

## Test / verify / run / build status

- Added regression tests in `test_promotion_gate.js` for duplicate-key and oversized-file rejection.
- Source integration is committed on the research branch.
- Attempted to clone and run `node test_promotion_gate.js` in the available shell, but the container runtime failed to start. The tests have **not** been executed successfully in this session.
- Latest observed exact-head Actions run before these changes was marked failed, with no usable step summaries/logs or artifacts. It does not diagnose the new code.
- Full `npm test`, `python3 test_descent.py`, and build status remain unverified.
- The branch has substantial divergence from `main`; reconcile it before promotion. Keep PR #89 draft and unmerged until exact-head CI logs and a same-run receipt are available.
