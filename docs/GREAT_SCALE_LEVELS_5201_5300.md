# Great Scale Levels 5201–5300 — Provenance claims are not authenticated provenance

## Descent question

The previous descent bound a review decision to a candidate commit and the pull request's observed head. A deeper question remains: what establishes that the evidence envelope was actually collected from GitHub, rather than assembled by someone who copied plausible field values into JSON?

A string such as `source: "github-actions-api"` is a claim inside the envelope. The structural gate can check that the claim has the expected value, but it cannot infer the origin of the bytes from the value itself.

## Indistinguishability result

Let V be a deterministic structural validator, and let x be a JSON evidence envelope that satisfies all schema and consistency checks. Consider two histories:

- H₁: a trusted collector obtains GitHub run, job, pull-request, and artifact records and serializes them into x.
- H₂: an untrusted actor constructs byte-identical x without making any GitHub API request.

If the validator receives only x and has no trusted cryptographic input distinguishing the histories, then

[
operatorname{bytes}(x_{H_1})=operatorname{bytes}(x_{H_2})
Longrightarrow V(x_{H_1})=V(x_{H_2}).
]

This is not a weakness unique to this code. A validator cannot distinguish identical inputs based only on a difference in their unobserved origin. Schema validation establishes structural consistency; it does not establish provenance authenticity.

## Assurance decomposition

Let S(x) mean structural validity, B(x) mean correct cross-field binding, A(x) mean authenticated collection, and F(x) mean freshness of the relevant platform state. Then a useful review predicate is

[
R(x)=S(x)land B(x)land A(x)land F(x).
]

The current `promotion_gate.js` implements structural checks and many bindings. It does not itself implement A(x), and its pull-request snapshot only provides a point-in-time input for F(x); freshness must be rechecked at action time. Consequently,

[
S(x)land B(x) 
otRightarrow R(x).
]

## Engineering consequences

1. Keep the current gate as a fail-closed structural policy, not a trust oracle.
2. Obtain run, job, step, artifact, and PR records from an authenticated GitHub API client in a trusted collector.
3. Bind the collected records to the exact repository, candidate SHA, run ID, artifact ID, and PR number/head.
4. If evidence crosses a trust boundary as a file, use an authenticated transport or a signed envelope with a verifier-controlled trust root. A signature is only useful if key custody and signer authorization are separately secured.
5. Re-fetch the PR head immediately before merge and require the expected SHA as an action-time precondition.
6. Preserve the original API response identifiers and retrieval metadata for audit. Do not treat a local receipt as independent proof that its own test process ran.

The gate's output remains `ELIGIBLE_FOR_PROMOTION_REVIEW`, and the caveat explicitly states that authenticated collection is a separate obligation. A test assertion now guards the presence of that caveat.

## Verification scope

Source-level checks can verify that the schema, binding conditions, and caveat are present. A small reference predicate can test the logical distinction between structural and authenticated evidence. Neither check authenticates GitHub records or substitutes for executing the repository test suite. The current hosted runner blocker means the committed JavaScript and Python suites remain unverified until a real run produces steps, logs, and the expected artifact on the exact head.

## Great Scale mapping

| Level | Mathematics | Science | Status |
|---|---|---|---|
| 5201 | Structural validity (S(x)) checks schema and local invariants. | Valid JSON can still be fabricated. | Gate contains strict schema checks; source-level inspection only. |
| 5202 | Binding (B(x)) relates repository, commit, run, job, receipt, artifact, and PR head. | Matching fields reduce accidental mismatch but do not prove their origin. | Implemented structurally; trusted collection remains external. |
| 5203 | Identical inputs imply identical deterministic validation outcomes. | A validator cannot observe an unencoded history of how identical bytes were produced. | Mathematical consequence under the stated input-only model. |
| 5204 | Full review eligibility requires (S\land B\land A\land F). | Authenticity and freshness require platform observations and a trusted collection/action boundary. | Authenticated collector and action-time SHA enforcement remain open obligations. |
| 5205–5300 | Next: define a verifiable collector contract, trust-root lifecycle, signed evidence envelope, and replay/freshness policy. | No empirical quantum-geometric claim follows from this software-assurance result. | Research frontier; full test execution remains blocked by CI runner availability. |

## Profound finding

**Provenance is not a property a JSON object can grant itself.** Structural validation can prove that a record is internally well-formed and consistently bound; authenticity requires a trusted observation or cryptographic verification rooted outside the record. Temporal safety then requires that the authenticated observation still matches the object at the moment of action.

The complete assurance chain is therefore not just “valid evidence.” It is structurally valid evidence, bound to the intended object, authentically collected, fresh enough for the decision, and enforced at action time. This is a software-assurance result, not a physical law.
