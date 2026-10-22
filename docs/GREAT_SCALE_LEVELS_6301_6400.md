# Great Scale — Levels 6301–6400: enforce structural limits before materialization

## Finding

Levels 6201–6300 introduced a JSON nesting cap, but review of call order exposed a subtle assurance mismatch: if the full payload is passed to `JSON.parse` before the scanner runs, the scanner's depth limit cannot constrain parser-time object-graph construction or parser-time behavior. A post-parse check is not a pre-parse guard.

This is a stage-ordering defect in the mitigation, not evidence that the JavaScript JSON parser is exploitable. The serialized byte cap still limits total input size; the improvement is to apply the explicit nesting/duplicate-key policy before constructing the full parsed object.

## Integration

- Moved the iterative structural scan before the full-payload `JSON.parse`.
- The scan checks depth before pushing object/array frames and rejects duplicate decoded object keys, including escaped-equivalent spellings.
- Individual key tokens are decoded with `JSON.parse`; the full document is parsed only after the scan succeeds.
- Normalized scanner syntax failures to `serialized input is not valid JSON`, while preserving explicit duplicate-key and nesting-limit errors.
- Existing regressions cover malformed JSON, duplicate keys, escaped-equivalent keys, and excessive nesting.
- The 1 MiB byte cap still runs first. An HTTP/API caller must enforce its own request-body cap before buffering bytes.

## Mathematics

Let (S) be the serialized document, (B=2^{20}) the byte cap, and (D_s=2D+8) the structural nesting cap for semantic limit (D=256). The ingress order is:

[
|S|_{UTF8}\le B
\quad\to\quad
\operatorname{scan}(S): d(S)\le D_s\ \land\ \text{unique decoded keys}
\quad\to\quad
\operatorname{parse}(S)
\quad\to\quad
\operatorname{verify}(P(S)).
]

The order matters: the precondition on (d(S)) must be checked before constructing (P(S)), not merely asserted afterward.

## Science and engineering interpretation

This is a general principle of staged assurance: a downstream validator cannot bound resources already consumed upstream. The control must precede the operation whose cost or ambiguity it is meant to constrain.

The layers now have distinct roles: transport bounds input buffering; the pre-scan bounds serialized structure and rejects duplicate keys; JSON parsing builds the representation; semantic validators bound AST/proof depth, node count, and derived work; evidence gates handle provenance and freshness. None substitutes for the others.

This is a software architecture finding, not a new physical law or empirical quantum-geometry result.

## Verification status

- Pre-parse scan ordering is integrated in `proof_kernel.js`.
- The exact-head Actions runs observed for recent commits report failure but do not expose usable step logs or artifacts. A retry was requested; that is not proof of test execution.
- No successful repository test/build run is verified. The ordering change, scanner behavior on malformed inputs, and the new nesting regression still require actual execution.
- PR #89 remains draft/unmerged. Reconcile the two commits behind `main` before promotion.
