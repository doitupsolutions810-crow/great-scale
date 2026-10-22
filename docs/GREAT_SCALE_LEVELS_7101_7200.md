# Great Scale — Levels 7101–7200: parser progress as a verification invariant

## Finding

The serialized proof boundary now performs a bounded, iterative structural scan before `JSON.parse`, so depth and duplicate-key checks happen before object-graph materialization. A further hardening obligation is that every malformed token path must fail closed without leaving the scanner at the same cursor position.

The scanner's scalar-token branch now explicitly rejects a required value when the current character is already a delimiter. Regression cases cover malformed arrays and objects such as `[,,]` and `{"a":,}`. This is a **defense-in-depth termination invariant**, not evidence of a demonstrated hang or remote exploit: review of the surrounding state transitions shows they also consume delimiters or change parser state.

## Integration

- Added a forward-progress assertion to the pre-parse scanner's scalar-token branch.
- Added malformed-delimiter regression cases to `test_proof_kernel.js`.
- Preserved the 1 MiB serialized-input limit, duplicate-key detection, and pre-materialization nesting limit.
- The scanner still delegates full JSON grammar validation to `JSON.parse` after the bounded scan; the scan is a resource and ambiguity preflight, not a replacement JSON parser.

## Mathematics

Let (n) be the input length and (i) the scanner cursor. A parser termination argument should make progress explicit. For each scalar-token branch that is required to consume a value, enforce:

[
i_{mathrm{after}}>i_{mathrm{before}}.
]

At the outer-loop level, each transition must either advance (i), pop a bounded container frame while consuming its closing delimiter, or change a finite parser state that forces subsequent input consumption. The frame depth is capped by (D_{max}=2D+8), where (D=256), and the input length is capped by (B_{max}=1{,}048{,}576) bytes.

These bounds establish finite input and finite nesting; the cursor/state invariant makes the termination obligation explicit. They do not establish logical proof soundness, provenance, or authenticity.

## Science and engineering interpretation

This is a software-verification result: a preflight parser is itself part of the trusted computing base. A bound on payload size does not automatically prove that every parser control-flow path terminates. The same design principle applies to protocol decoders, certificate readers, and static analyzers: input limits, grammar validity, semantic validity, and provenance are separate properties.

No empirical or physical quantum-geometry conclusion follows from this software change.

## Test / verify / run / build status

- **Source integration:** scanner guard and regression tests are committed on the research branch.
- **Regression intent:** malformed delimiters must be rejected with the normalized invalid-JSON error rather than accepted by the preflight scan.
- **Isolated scanner harness:** 9/9 cases passed for valid nested JSON, duplicate keys, escaped-equivalent keys, malformed delimiters/keys/colon, depth rejection, and canonically distinct Unicode strings. This exercised an equivalent scanner implementation in the available JS execution environment, not the repository file or full `npm test` suite.
- **Repository test execution:** not verified. GitHub Actions runs have repeatedly reported failure without usable step logs or artifacts; those statuses do not establish that assertions executed or failed.
- **Build:** not run/verified.
- **Promotion:** keep the PR draft and unmerged until the exact current SHA has actual runner steps, retrievable logs, both required suites passing, a same-run receipt artifact, and reconciled branch divergence.

## Great Scale map

| Level | Mathematics | Engineering meaning | Status / required evidence |
|---|---|---|---|
| 7101 | (i_{after}>i_{before}) on required scalar consumption | Fail closed when a value position contains a delimiter | Guard and regression source present; execution unverified |
| 7110 | (D_{max}=2D+8) | Bound preflight container-stack depth | Source present; full boundary tests unexecuted |
| 7120 | (Ble1{,}048{,}576) bytes | Bound serialized payload before scanning | Source present; transport-layer request cap remains a separate requirement |
| 7130 | duplicate decoded keys are forbidden per object | Avoid ambiguous claim interpretation | Scanner and duplicate-key tests present; execution unverified |
| 7200 | structural preflight (
e) semantic proof verification | Keep parser, proof checker, provenance, and execution evidence as separate assurance gates | Research-only; no passing exact-head CI receipt established |
