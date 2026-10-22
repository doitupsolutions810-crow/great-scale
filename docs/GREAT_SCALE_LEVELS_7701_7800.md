# Great Scale — Levels 7701–7800: bound aggregate JSON values before materialization

## Finding

The serialized scanner already capped bytes, nesting depth, and distinct object keys before calling `JSON.parse`. A deeper review found that arrays were still unbounded by element count. A payload below the 1 MiB byte limit could contain hundreds of thousands of small scalar elements, or many individually moderate arrays. The scanner would traverse these tokens and then allow the full parser to allocate a large array/object graph before the proof schema or AST validator rejected the input.

This is a bounded resource-amplification gap in the serialized ingress path, not evidence of a deployed remote exploit. The important distinction is that byte count constrains input volume but does not directly constrain the number of materialized JavaScript values.

## Integration

- Added `MAX_SERIALIZED_ARRAY_ITEMS = MAX_NODES` (10,000) and rejects an array's next item before full JSON parsing.
- Added `MAX_SERIALIZED_JSON_VALUES = MAX_NODES * 4` (40,000) and charges each serialized value/container start during the iterative pre-scan.
- Kept object keys separately bounded by `MAX_SERIALIZED_OBJECT_KEYS = 4`, nesting by `MAX_SERIALIZED_JSON_DEPTH = 520`, and payload bytes by `MAX_INPUT_BYTES = 1,048,576`.
- Exported both new constants and added regressions for one over-limit flat array and aggregate values spread across individually bounded arrays.
- Preserved explicit limit errors through `parseBoundedJson` rather than collapsing them into generic malformed-JSON errors.

The aggregate value limit is a conservative ingress policy. It is distinct from semantic node budgets: JSON values include object/array containers and scalar tokens, while the proof kernel counts formula/proof nodes according to its own rules.

## Mathematics

Let (J) be the serialized input, (B) the byte limit, (D_s) the structural depth limit, (W) the object-key limit, (A) the per-array item limit, and (V) the aggregate JSON value limit. The preflight now enforces:

\[
|J|_{UTF8} \le B,\quad depth(J)\le D_s,\quad
\forall o:\ keys(o)\le W,\quad
\forall a:\ items(a)\le A,\quad values(J)\le V.
\]

For the current kernel: (B=1{,}048{,}576), (D_s=520), (W=4), (A=10{,}000), and (V=40{,}000).

A bounded input length gives a finite upper bound on scan time, but a value-count limit reduces the maximum representation expansion more directly. The limits are complementary, not interchangeable.

## Science and engineering interpretation

The general principle is **resource safety must follow the representation through every expansion step**. A byte string becomes tokens; tokens become arrays and objects; those structures become formulas and proof trees; proof rules generate derived comparisons and contexts. Each transition has its own cost model.

This change improves the software ingress contract. It does not establish proof-system soundness, authenticated provenance, empirical validation, or a new physical quantum-geometry law.

## Great Scale mapping

| Level | Mathematics | Engineering / science meaning | Test / verification gate |
|---|---|---|---|
| 7301 | (items(a)\le 10{,}000) | No single array can expand beyond the supported ingress width | 10,001-item array must fail before semantic verification |
| 7310 | (values(J)\le 40{,}000) | Bound aggregate parsed-value count, not just payload bytes | Values spread across multiple arrays must fail at aggregate limit |
| 7320 | (bytes, depth, keys, items, values) are independent bounds | No one resource limit substitutes for another | Boundary tests for each independent dimension |
| 7330 | Preflight rejection precedes (parse(J)) | Reject costly representations before materializing the full graph | Confirm scanner call order in source and test errors |
| 7400 | Representation validity (\ne) logical validity (\ne) evidence authenticity | Keep parsing, proof checking, and provenance as distinct gates | Exact-head official suites and authenticated evidence required |

## Test / verify / run / build status

- **Source inspection:** the scanner and exported constants were reviewed on the research branch; aggregate-value and per-array checks were added before the full `JSON.parse` call.
- **Regression source:** tests now cover a 10,001-item array and more than 40,000 values spread across arrays that are individually under the item limit.
- **Isolated scanner harness:** 8/8 bounded cases passed in the available JavaScript execution environment for valid nested JSON, duplicate and escaped-equivalent keys, malformed delimiter rejection, depth cap, per-array cap, aggregate-value cap, and canonically distinct Unicode keys. This exercised an equivalent scanner harness, not the committed repository file or the full repository suite.
- **Repository execution:** these new repository tests have not yet been confirmed as executed in a real repository runner.
- **Official test suites and build:** no passing result is claimed. The previously inspected CI failure had no usable step logs/artifacts; it cannot establish that assertions ran or failed.
- **Integration status:** branch remains ahead of and behind `main`; the exact current head and divergence must be reconciled before promotion. Keep PR #89 draft/unmerged until exact-head test logs, both required suites, receipt, and runner provenance are available.

## Conclusion

**The profound finding is that input size is not the same as representation complexity.** A secure serialized boundary must bound bytes, nesting, key width, array width, and aggregate values before parsing; semantic proof budgets only begin after that representation exists.
