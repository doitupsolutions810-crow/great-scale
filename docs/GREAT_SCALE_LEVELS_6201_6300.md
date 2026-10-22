# Great Scale — Levels 6201–6300: bound representation depth before verification

## Finding

The 1 MiB serialized-input limit bounds payload bytes, but a compact document can still be deeply nested. The duplicate-key scanner is iterative, yet its stack grows with JSON nesting. Before this change, the scanner could build a large stack before the proof/formula validators applied their own depth limits.

This is a pre-semantic resource-boundary gap. It is not a demonstrated remote exploit, and its practical severity depends on how the serialized entry points are exposed and what resource limits surround them.

## Integration

- Added `MAX_SERIALIZED_JSON_DEPTH = 2 * MAX_DEPTH + 8`.
- The iterative duplicate-key scanner now checks nesting before pushing each object/array frame.
- The separate limit accounts for a proof tree and formula AST being nested within the same JSON document, plus envelope/context layers.
- Exported the limit and added a regression test that sends a valid but excessively nested JSON array through `checkSerialized`, expecting a fail-closed depth-limit error.
- The scanner runs after `JSON.parse` has established syntax validity, so this specifically bounds scanner-stack growth and later processing; it does not replace a transport request-body cap or a parser-level limit.

## Mathematics

Let (d(J)) denote maximum object/array nesting depth in serialized JSON (J). The serialized boundary now requires

[
|J|_{UTF8} \le 2^{20},\qquad d(J) \le 2D+8,
]

where (D=256) is the proof/formula semantic depth limit. These constraints bound different dimensions: byte size constrains representation volume, while nesting constrains stack-like structural growth.

The depth condition is deliberately not identified with logical proof depth: serialized structure includes envelopes and can combine proof-node nesting with formula-AST nesting.

## Science and engineering interpretation

A resource policy is compositional only when each earlier stage is bounded at the stage where its resources are consumed. A downstream invariant cannot retroactively protect an upstream parser or representation builder. The general pattern is:

1. Bound transport bytes before buffering.
2. Bound parser/representation nesting.
3. Reject ambiguous serialized representations.
4. Apply schema, AST, proof, and derived-work budgets.
5. Verify logic and bind claims to authenticated evidence.

These layers are complementary rather than interchangeable. This result is about software assurance, not evidence for a physical quantum-geometry law.

## Verification status

- Source integration and a regression case are committed on the research branch.
- The latest exact-head workflow retry was requested, but no successful execution evidence has yet been observed. A queued or failed run without inspectable step logs is not a test pass.
- The new nesting test and build remain unverified until a runner executes them on the exact head and returns inspectable logs.
- Keep PR #89 draft and unmerged; reconcile the branch's two commits behind `main` before promotion.
