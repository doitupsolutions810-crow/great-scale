# Great Scale Levels 5501–5600: Stable Proof Certificates Under Mutation

**Track:** \`research/kernel-hardening-4401-4500\`  
**Scope:** proof-result ownership, aliasing, and post-validation mutation  
**Implementation status:** detached formula copying and recursive freezing integrated with regression tests; actual repository test execution remains blocked by hosted CI evidence failure.

## 1. Deeper repository finding

The previous level made proof-input validation descriptor-first, so ordinary accessor-backed fields are rejected without executing getters. That closes one input-side-effect gap, but it does not by itself make the *result* of checking a proof stable.

In the primary kernel, the \`assume\` inference previously returned the supplied formula array directly as both conclusion and context member. A caller retaining that array could mutate it after \`check()\` returned. The returned object would then no longer necessarily represent the formula that was inspected when the proof was checked. Auxiliary formulas used by disjunction introduction and implication introduction also needed an explicit ownership boundary.

The next assurance property is:

> **A successful check returns a kernel-owned, stable certificate whose meaning cannot be changed by mutating the original proof input or by mutating the returned result.**

## 2. Mathematical formulation

Let \(p\) be an accepted proof input and \(V(p)=r\) the checker result. Let \(\llbracket r\rrbracket\) denote the result's represented conclusion and assumption context.

### Input non-aliasing

For any permitted mutation \(\mu\) of caller-owned input arrays after checking,

\[
\llbracket V(p)\rrbracket
=
\llbracket V(\mu(p))\rrbracket
\]

is intended only when \(\mu\) happens after the original call and the left-hand side is the already returned result. More directly, if \(r=V(p)\) and the caller later mutates \(p\) into \(p'\), then

\[
\llbracket r\rrbracket_{\text{after }p\to p'}
=
\llbracket r\rrbracket_{\text{at return}}.
\]

This requires that accepted formula data be copied into kernel-owned arrays before those arrays are exposed as checked conclusions or contexts.

### Result immutability

For a returned result graph \(r\), recursive freezing establishes that ordinary strict-mode writes to its own frozen objects fail and do not change its structure:

\[
\operatorname{FrozenClosure}(r)
\Rightarrow
\operatorname{Mutate}(r)\text{ cannot alter its represented data}.
\]

These are object-ownership and representation-stability properties. They do not establish logical soundness by themselves, and they do not make a mutable proof input immutable.

## 3. Integrated change

The current branch now:

- Adds \`copyFormula\`, which reads formula arrays through the strict descriptor-based array reader and builds new formula arrays.
- Copies the formula in the \`assume\` rule rather than returning the caller-owned formula array.
- Copies auxiliary formulas used by \`impI\`, \`orIL\`, and \`orIR\` before they enter the returned derivation.
- Recursively freezes the completed proof-check result graph before returning it from \`check()\`. The formulas that can enter that result graph through supported rules are copied first, avoiding freezing the caller's original formula arrays as a side effect.
- Adds three regression cases in \`test_proof_kernel.js\`: mutate the original formula after checking, attempt to mutate a frozen result, and mutate an auxiliary disjunction formula after checking.

The change intentionally leaves the checker API and the represented propositional rules unchanged. It strengthens ownership and post-check stability.

## 4. Important boundaries and caveats

1. **Proxy objects remain outside the stated guarantee.** Reflection on JavaScript Proxies can execute traps. Descriptor-first validation and copying do not establish side-effect freedom for arbitrary adversarial Proxy values.
2. **The result is a JavaScript object graph, not a signed external certificate.** Freezing prevents ordinary in-process mutation of this returned graph; it does not authenticate provenance, survive serialization as an integrity property, or replace the promotion gate's exact-SHA and platform-evidence checks.
3. **Logical correctness remains a separate obligation.** The kernel must still implement the inference rules and context discharge correctly. Immutability preserves the checked representation; it cannot repair an unsound inference rule.
4. **Test execution is not inferred from source presence.** The new regressions are committed but remain unverified until \`npm test\` and \`python3 test_descent.py\` run on the exact commit with retrievable logs and a same-run receipt artifact.

## 5. Great Scale mapping

| Level | Mathematics | Science | Status |
|---|---|---|---|
| 5501–5510 | A checked result must not alias caller-owned formula arrays | Mutating the source after checking must not retroactively change the checked conclusion | \`copyFormula\` integrated; regression authored |
| 5511–5520 | \(\llbracket r\rrbracket_{\mathrm{after}}=\llbracket r\rrbracket_{\mathrm{return}}\) | The represented certificate must remain stable after the validation call | Ownership invariant formalized |
| 5521–5530 | A result's reachable object graph is recursively frozen | Ordinary writes to returned result arrays/objects should fail rather than silently change the result | \`freezeResult\` integrated |
| 5531–5540 | Inference rules must copy every input-derived formula that escapes into the result | The \`assume\`, \`impI\`, \`orIL\`, and \`orIR\` paths are relevant aliasing boundaries | Supported paths updated |
| 5541–5550 | Input non-aliasing and result immutability are separate conditions | Copying protects against later source mutation; freezing protects the returned graph | Both conditions represented in code |
| 5551–5560 | Representation stability does not imply derivation soundness | A stable certificate can still encode an invalid inference if rules are wrong | Assurance obligations kept separate |
| 5561–5570 | In-process freezing is not external provenance authentication | Serialization, signing, and trust decisions need their own policy | Scope explicitly bounded |
| 5571–5580 | Mutation-after-check is a falsifiable adversarial property | Tests must mutate the original formula and auxiliary formula after checking | Three regressions authored |
| 5581–5590 | A test source is not an execution trace | Only an exact-SHA run with logs can establish test outcomes | Hosted verification still blocked |
| 5591–5600 | Proof-certificate integrity requires controlled input, detached representation, and stable output | This is a software verification result, not empirical confirmation of quantum geometry | Integrated, test execution pending |

## 6. Verification record

The repository's latest known hosted Actions run remains a failure with no useful step summaries, no retrievable log URL, and no receipt artifact. Previous retry reproduced the same pattern. Local shell execution was unavailable in the current session.

Therefore, this note records the implementation and authored regression cases, **not a passing test run**. Required verification remains:

- Run \`npm test\` on the exact head SHA.
- Run \`python3 test_descent.py\` on the same SHA.
- Retain platform-observed runner identity, successful step summaries, retrievable logs, and the same-run verification receipt.
- Re-evaluate the promotion gate against authenticated, current evidence.

## 7. Conclusion

The deeper result is that **a proof checker must stabilize the object it claims to have checked**. Getter-safe input handling prevents validation from executing ordinary accessors; detached copying and recursive freezing prevent later mutation from changing the returned certificate representation. These are complementary layers, not interchangeable ones.

The implementation now encodes this stability boundary in the primary kernel and adds targeted regressions. Until the exact committed suites execute successfully, the implementation remains integrated but not repository-test-verified. No new physical law or empirical quantum-geometric finding follows from this software-assurance result.
