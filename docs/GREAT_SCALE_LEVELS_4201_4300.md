# Great Scale research note: Levels 4201–4300

**Status:** research/design note; finite reference-model tests added. Not a general proof checker and not evidence for a physical quantum-geometry law.

## Descent result

The Level 4100 principle was that a conclusion must not exceed the scope warranted by its premises unless a valid scope-transfer theorem justifies the extension. Levels 4201–4300 sharpen this into a typed evidence-transfer contract.

A transfer is represented schematically by

`f : (S, \Gamma_S) \to (T, \Gamma_T)`

together with a preservation obligation `\pi_f` establishing that the inference relevant to the claim is preserved under `f`. The notation is schematic: a production formalization must define the logic, scope semantics, assumptions, and checker.

Composition is permitted only when the endpoint types align:

`f : S -> T,  g : T -> U  =>  g o f : S -> U`

and the preservation obligations for both maps are discharged in a sound formal system. A string label such as `preservation: "checked"` is only a test fixture in this reference suite; it is not itself a proof.

## Quantifier traps

- If `S ⊆ T`, then `∀x∈T, P(x)` entails `∀x∈S, P(x)`; the reverse does not generally hold.
- If `S ⊆ T`, then a witness for `∃x∈S, P(x)` is also a witness in `T`; the reverse does not generally hold.
- Thus, scope transport is rule-dependent. A universal claim and an existential witness do not obey the same widening/narrowing rule.

## Dimensional typing

A conversion such as `1 m = 100 cm` is permitted only under a registered, checked conversion that preserves the dimension. A length-to-time conversion is rejected. Real implementations must validate units and conversion constants rather than trust metadata.

## Finite reference tests

`test_scope_transfer.js` contains 16 checks covering:
- universal and existential quantifier scope behavior;
- compatible and incompatible morphism composition;
- missing preservation obligations;
- conclusion scope bounded by the intersection of premise scopes;
- transfer certificate identity and binding;
- registered unit conversion, dimensional mismatch, missing conversion, and self-asserted conversion.

The test cases were added to `npm test` on branch `research/typed-scope-4101-4300`. They have not been treated as passing until the execution environment reports a run. If CI is unavailable, run:

```bash
npm test
python3 test_descent.py
npm run all
```

## Profound candidate finding

**Scope is a type on evidence, and evidence transport is a typed morphism with a preservation obligation.** Inference validity alone is insufficient: the scope of the conclusion must be justified by the inference rule and the actual transfer certificate.

Absent an independently justified transfer theorem, require

`S_Q ⊆ ⋂ᵢ Sᵢ`

for premise scopes `Sᵢ` and conclusion scope `S_Q`.

## Assurance boundary

These are reference-model policy tests. They do not establish that a registry is authentic, that a certificate is mathematically sound, that the checker is correct, or that the proposed Quantum Geometry Mathematics hypothesis describes physical reality. The next formal step is to encode the rules in a specified proof assistant or small, independently reviewed kernel and bind certificates to canonical claim, assumptions, source/target scope, logic, and checker version.
