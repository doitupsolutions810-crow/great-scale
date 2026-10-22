# Great Scale — Levels 6101–6200: one serialized meaning

## Finding

A byte limit and an exact post-parse schema do not guarantee an unambiguous serialized claim. JavaScript `JSON.parse` silently accepts duplicate object keys and retains the last occurrence. Thus, for example, an envelope can contain two `expectedConclusion` fields. A downstream signer, logger, auditor, or implementation using a first-key-wins parser could interpret the same bytes differently from this kernel.

Escaped-equivalent names are also duplicates: `"expectedConclusion"` and `"expectedConclu\\u0073ion"` decode to the same property name. Checking keys only after `JSON.parse` cannot recover the duplicate that was discarded.

This is a parser-differential risk, not evidence of an observed exploit in a deployed service. Its significance depends on whether other components interpret or attest to the same serialized payload.

## Integration

- Added an iterative duplicate-key scan after the existing byte limit and successful JSON syntax parse.
- The scanner decodes object-key tokens before comparison, so escaped-equivalent keys collide.
- Applied the check to the common bounded JSON parser; therefore all three serialized entry points share the policy.
- Added regression coverage for duplicate keys in a proof object and escaped-equivalent duplicate keys in a claim envelope.
- Kept parsing syntax validation separate from semantic proof checking: duplicate rejection establishes one representation, not logical validity.

## Mathematics

Let (J) be a serialized JSON document and let (P(J)) be its parsed object graph. Ordinary parsing is not injective over raw documents: distinct strings can yield the same parsed object because duplicate earlier keys are discarded. A security boundary should reject any object scope whose decoded key sequence is not unique:

[
\forall o,\quad i\ne j \implies k_i(o)\ne k_j(o).
]

This condition removes one source of parser ambiguity. It does not authenticate the producer, bind the payload to a commit, or prove the inference rules sound.

## Science and engineering interpretation

The deeper principle is that **bounded representation is not the same as canonical representation**. Resource bounds constrain size and work; duplicate-key rejection constrains interpretation; proof checking constrains logical validity; authenticated provenance constrains who or what produced the evidence. These are independent assurance dimensions.

No physical quantum-geometry claim follows from this software result.

## Verification status

- Source edits and regression tests have been committed to the research branch.
- The latest prior workflow run failed without retrievable job-step details or artifacts. A rerun of that failed job was requested, but that does not verify the newer commits.
- The new scanner and tests have not yet been executed in a confirmed runner with retrievable logs.
- Do not mark the suite or build as passed until CI runs on the exact current head and the results are inspectable.
- The branch remains divergent from `main`; reconcile the two commits behind before promotion.
