# Great Scale — Levels 6001–6100: bound the representation boundary

## Finding

The proof kernel's node/depth limits begin after the caller has materialized JavaScript objects. `readDataObject` enumerates all own keys with `Reflect.ownKeys` before rejecting a record wider than four fields. For arrays, the length is checked before key enumeration, but an in-process ordinary array can still have many custom own properties and require enumeration before rejection. The logical AST limit does not bound this pre-validation representation work.

This is a boundary finding, not a demonstrated remote exploit. It matters when untrusted callers can pass arbitrary live JavaScript objects directly. Proxies can execute traps during reflection and require an additional process/serialization trust boundary.

## Integration

- Added `MAX_INPUT_BYTES = 1,048,576`.
- Added `parseBoundedJson`, which accepts only strings, rejects oversized code-unit counts before scanning UTF-8 byte length, rejects payloads above the byte limit, and parses only after the size checks.
- Added `checkSerialized` as the bounded serialized entry point for proof checking.
- Added `checkBoundSerialized` for an exact-schema claim envelope and `tautologyUnderContextSerialized` for an exact-schema truth-table envelope.
- Added regression tests for valid serialized proof checking, non-string rejection, oversize rejection, malformed JSON, exact claim binding, extra envelope fields, and the truth-table wrapper.
- Kept the object-taking APIs for compatibility. Their callers must ensure that the object is already bounded before invoking them; the new serialized wrappers are the safer ingress boundary for untrusted JSON.

## Mathematics

Let (s) be the UTF-16 code-unit length and (b) the UTF-8 byte length of the serialized input. The ingress enforces
[
s \leq B \quad\text{and}\quad b \leq B,
\qquad B=1{,}048{,}576,
]
before JSON parsing. Therefore the verifier's parser-side work is limited to an input string whose size is bounded by (B), after which AST node/depth and derived-work budgets apply.

This does not imply a precise wall-clock bound. It also cannot retroactively bound memory already consumed by the caller to construct an object before calling the object API. If inputs arrive over a network, the transport/server must enforce a request-body limit before buffering the entire body.

## Science and engineering interpretation

This is a layered resource-boundary principle: the size of a mathematical object, the cost of representing/decoding it, and the cost of checking it are distinct quantities. A proof-kernel node budget alone does not account for work spent acquiring or enumerating the representation.

No physical quantum-geometry claim follows from this software result.

## Evidence status

- Source and tests committed to the research branch.
- Source-level contract checks must be rerun against the latest commit.
- The new regression and full repository suites are not considered passed until an actual runner executes them on the exact head with retrievable logs.
- Build remains unverified until execution evidence exists.
- The object-taking APIs remain compatible and do not claim protection against an already-materialized arbitrarily wide object; callers handling untrusted JSON should use the bounded serialized wrappers and enforce a transport request-size limit.
