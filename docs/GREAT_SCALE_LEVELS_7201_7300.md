# Great Scale — Levels 7201–7300: bound structural amplification before parsing

## Finding

The serialized ingress path already caps input at 1 MiB and rejects excessive nesting and duplicate keys before calling `JSON.parse`. However, the scanner accumulated every distinct object key in a per-object `Set` without limiting the number of keys. A bounded but deliberately wide object could therefore allocate a large key set during the scan and then cause `JSON.parse` to allocate a second object representation before the proof schema rejected the object.

This is a resource-amplification opportunity within the existing byte cap, not a demonstrated remote exploit. The relevant invariant is that all supported object records are narrow: proof nodes have at most four fields, and the serialized claim/oracle envelopes have fewer.

## Integration

- Added `MAX_SERIALIZED_OBJECT_KEYS = 4`.
- The pre-parse scanner now rejects the fifth distinct decoded key in any object, before parsing the full object graph.
- The bounded parser preserves the explicit width-limit error rather than disguising it as malformed JSON.
- Exported the constant and added a regression case using a five-key proof object.
- Existing duplicate-key, nesting, byte-limit, schema, and semantic proof checks remain independent layers.

## Mathematics

Let (B) be the serialized byte budget, (D) the maximum container nesting depth, and (W) the maximum number of decoded keys per object. The ingress scanner now enforces:

[
|J|_{UTF8} \le B,\qquad depth(J) \le D,\qquad
\forall o\in Objects(J): keys(o)\le W.
]

For the current proof-kernel data contract, (B=1{,}048{,}576), (D=520), and (W=4). These are representation constraints, not a proof of a linear heap bound or of logical soundness; they remove an avoidable source of object-width amplification before materialization.

## Science and engineering interpretation

The broader principle is **bound each representation before expanding it into the next representation**. Input bytes, nesting, object width, AST nodes, derived kernel work, and truth-table evaluation work are distinct resource dimensions. A bound on one does not automatically bound the others.

This is a software-assurance result. It does not establish a new physical law or empirically validate quantum geometry.

## Verification status

- Source changes committed to the research branch.
- A regression test was added to `test_proof_kernel.js`.
- Source inspection confirms the new constant is checked while scanning object keys and the width error is preserved by `parseBoundedJson`.
- The regression and full repository suites have not been executed in a confirmed runner with inspectable logs. No build pass is claimed.
- Keep PR #89 draft/unmerged until exact-head test execution, retrievable logs, a same-run receipt artifact, and branch-divergence reconciliation are complete.
