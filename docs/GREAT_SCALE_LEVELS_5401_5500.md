# Great Scale Levels 5401–5500: Inert Proof Inputs and Side-Effect-Free Validation

**Track:** \`research/kernel-hardening-4401-4500\`  
**Scope:** proof-kernel and truth-table checker input boundaries  
**Implementation status:** hardening changes and regression tests are committed on this branch; repository execution has not yet been verified.

## 1. Deeper repository finding

The previous levels hardened field names, AST size, recursion depth, and Boolean assignments. Deeper inspection found that those controls were not uniformly enforced at the JavaScript property-access boundary.

In the primary \`proof_kernel.js\`, proof nodes were checked with \`Object.keys\` and then read through expressions such as \`p.rule\` and \`p.formula\`. An own accessor property can have an expected name and still execute arbitrary getter code when read. A schema may therefore look correct by its key names while validation itself invokes behavior supplied by the input.

The truth-table checker already rejects accessors in formula and claim records, but its evaluator also read a valuation as \`valuation[name]\` after checking property ownership. An own getter satisfies an ownership check and is executed by that read.

The next assurance boundary is:

> **A proof term must be inert data; validation must not execute its accessors in order to decide whether it is valid.**

This is a software trust-boundary issue, not a new physical result.

## 2. Mathematical statement

Let \(\mathcal D\) be the intended JSON-like input domain: finite, non-proxy JavaScript values composed of permitted strings, plain records, and ordinary dense arrays. Record fields must be own data properties; formula arrays must have the ordinary array prototype and contain only dense numeric data elements plus their standard \`length\`; unexpected fields, accessors, sparse slots, symbols, and custom array properties are rejected.

For a validator \(V\), define \(G(V,x)\) as the number of getter invocations caused by reading values from an ordinary input \(x\) while validation takes place. The target invariant is

\[
\forall x\in\mathcal D,\qquad G(V,x)=0.
\]

Invalid accessor-backed input must be rejected by inspecting descriptors before the corresponding value is read. For a valid input, semantic evaluation must only consume values that have crossed this schema boundary.

This property is distinct from logical soundness. Logical soundness asks whether accepted derivations preserve truth under the formal semantics. Inert-input validation asks whether the act of deciding acceptance runs attacker-provided property accessors. A sound inference rule does not compensate for an unsafe input boundary.

### Why an own-property test is insufficient

An ownership predicate such as \(\operatorname{hasOwn}(x,k)\) answers whether \(k\) is an own property. It does not say whether reading \(x[k]\) executes a getter. Therefore

\[
\operatorname{Own}(x,k)\not\Rightarrow
\operatorname{DataProperty}(x,k).
\]

The safe check is descriptor-based: establish that the descriptor contains a data \`value\`, and use that value, rather than evaluating the property expression.

## 3. Integrated hardening

The current branch changes:

- **\`proof_kernel.js\`:** adds plain-record and dense-array readers that inspect own property descriptors before reading fields. Proof nodes, formula arrays, and expected/context arrays reject accessor-backed entries and malformed array structures. Truth assignment reads now inspect the own descriptor and reject accessors before consuming the Boolean value.
- **Special-key normalization:** record fields are copied with \`Object.defineProperty\`, rather than ordinary assignment. This prevents an own \`__proto__\` input key from being silently interpreted as a prototype mutation during normalization and disappearing from the later schema check.
- **\`test_proof_kernel.js\`:** adds regression cases proving that proof-node getters, formula-array getters, and valuation getters are rejected without invocation; sparse expected contexts are rejected; and an own \`__proto__\` field cannot disappear during normalization.
- **\`test_truth_table_kernel.js\`:** changes valuation reading to use an own data-property descriptor and adds a regression case showing that an accessor-backed Boolean assignment is rejected without executing its getter.

These are source integrations and authored regression tests. They are not represented here as passing tests until the committed test suite actually runs.

## 4. Invariant and limits

For ordinary non-proxy objects, descriptor-first processing supports the invariant in Section 2 at the inspected proof/AST/context/valuation fields. The validation path rejects accessor descriptors without evaluating them, and normalization preserves special property names as own keys so the exact-schema check can reject them.

JavaScript proxies are a limitation: operations such as \`Object.getPrototypeOf\`, \`Reflect.ownKeys\`, and \`Object.getOwnPropertyDescriptor\` can invoke proxy traps. This code does **not** prove side-effect freedom for arbitrary hostile in-process Proxy objects, nor does it establish isolation from all JavaScript object behaviors. If the input crosses an adversarial trust boundary, prefer a serialized data protocol and a carefully controlled parser/process boundary. If duplicate JSON member names matter for the security policy, use a parser that explicitly detects them; ordinary \`JSON.parse\` does not preserve duplicate-key history.

The kernel remains an educational finite propositional reference implementation, not a production-certified theorem prover or a general proof system. The finite truth-table oracle continues to be restricted to its documented grammar and limits.

## 5. Regression / verification contract

The newly authored cases cover:

1. A proof node with getter-backed \`rule\` and \`formula\` is rejected without either getter running.
2. A formula AST array with a getter-backed operand is rejected without that getter running.
3. The primary kernel's truth-assignment accessor is rejected without invocation.
4. A sparse expected-context array fails closed.
5. An own \`__proto__\` field cannot be erased by normalization to evade exact schema validation.
6. The independent truth-table evaluator rejects a getter-backed Boolean assignment without invoking it.

Existing regression tests continue to cover inference-rule correctness, context binding, AST/proof recursion limits, aggregate node budgets, truth-table work budgets, and malformed schemas. The required next verification is execution of \`npm test\` and \`python3 test_descent.py\` against the exact current commit, with readable Actions steps/logs and a commit-bound receipt artifact.

The current environment could not execute a local shell. The most recent known hosted Actions behavior has been a job failure before useful step/log/artifact evidence appeared. Until a fresh exact-head run supplies actual execution evidence, the new regression tests remain **authored but unverified**.

## 6. Great Scale mapping

| Level | Mathematics | Science | Status |
|---|---|---|---|
| 5401–5410 | Separate \(\operatorname{Own}(x,k)\) from \(\operatorname{DataProperty}(x,k)\) | An own getter may execute behavior when read despite passing an ownership test | Gap identified; code hardened |
| 5411–5420 | Require \(G(V,x)=0\) for accessor invocation on the specified ordinary data-object domain | Validation itself should not execute accessor behavior from input | Invariant formalized; adversarial cases authored |
| 5421–5430 | Dense arrays and exact schema constrain the admissible input language | Sparse slots, custom keys, symbols, and accessors should not acquire unintended semantics | Strict readers integrated; repository tests not yet run |
| 5431–5440 | Descriptor-based normalization preserves schema identity | Ordinary assignment to \`__proto__\` can alter a clone's prototype rather than preserve the key as data | Normalization changed; regression authored |
| 5441–5450 | Independent evaluators must enforce the same data/value boundary for truth assignments | An oracle can share an input-side-effect weakness even when formula AST checks are strict | Truth-table valuation reader hardened |
| 5451–5460 | Logical soundness and inert-input processing are independent obligations | Correct inference does not imply safe parsing or validation | Assurance decomposition stated |
| 5461–5470 | The invariant is scoped to ordinary non-proxy objects, not arbitrary JavaScript values | Proxy reflection traps require a separate process/serialization trust boundary | Limitation explicit |
| 5471–5480 | Malformed representations should fail before semantic evaluation | Adversarial regressions make the property falsifiable | Tests authored; actual execution pending |
| 5481–5490 | Assurance claims must be bound to the exact code revision and observed run | Source inspection cannot establish hosted execution | Waiting for retrievable exact-head CI evidence |
| 5491–5500 | Proof-kernel acceptance includes both derivation semantics and input-boundary constraints | This is a software-assurance result, not empirical evidence for quantum geometry | Scope preserved; no physical law claimed |

## 7. Conclusion

The deeper finding is that **formal correctness and validation purity are different dimensions of a proof kernel**. Even an inference system with sound rules can have an unsafe boundary if checking the shape of a purported proof executes code embedded in that input. Conversely, rejecting getter-backed records is not a proof of logical soundness; it is a prerequisite for a clearly defined, inert input semantics.

The implementation now addresses accessor reads and special-key normalization in the inspected paths and includes tests designed to demonstrate those properties. Completion of the verification claim still depends on executing those tests on the exact committed SHA. No new physical law or empirical quantum-geometric result follows from this work.
