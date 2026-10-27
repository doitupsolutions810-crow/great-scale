# Descent CLXXI — source reachability is not execution proof

## Finding

The test-manifest auditor itself became an assurance-sensitive component. A verifier can be present in CI and still overstate whether a test executes. The previous implementation had several edge cases:

1. A regression fixture contained doubled backslashes before n, writing literal backslash-n tokens into the temporary Python file instead of line breaks. The fixture therefore raised SyntaxError before exercising the intended dead-branch assertion.
2. The loop-dispatch heuristic searched the entire ast.For subtree with ast.walk. It could see a loop-target call inside if False or inside a nested helper that the program never invokes, and misclassify registry tests as executed.
3. The general descendant scan could count a test call under a literal while False loop.
4. A bare call to an async def test creates a coroutine object. Without awaiting or scheduling it, the test body does not execute; a name-level call scan can nevertheless count it.

These are not merely test-counting mistakes. They are failures in the evidence-producing mechanism that is supposed to certify test reachability.

## Mitigation integrated on this branch

The current branch now:

- Corrects the dead-branch fixture so it writes a syntactically valid Python source file.
- Checks loop-target dispatch through a visitor that follows literal boolean if branches and does not descend into nested function, async-function, lambda, or class bodies.
- Handles literal while False as a dead body and inspects only its else branch.
- Treats top-level asynchronous test definitions as not proven executed by this synchronous direct-runner auditor. This is intentionally fail-closed: it may require an explicitly supported async runner in future, rather than silently treating a coroutine creation as test execution.
- Adds regression cases for dead if and while branches, loop dispatch in a dead branch, loop dispatch in an uncalled helper, bare async invocation, direct invocation, registry dispatch, and bare name references.

This is a syntactic reachability guard, not a general Python control-flow proof. The audit deliberately supports a limited main-guard/direct-call/registry pattern. New runner patterns must receive explicit tests before they can count as proof.

## Reconstructed local validation

A copied-source harness for the patched algorithm produced the expected results on **8/8 cases**:

| Case | Expected auditor result | Observed |
|---|---|---|
| Direct synchronous call | accepted | pass |
| Call only in if False | missing | pass |
| Call only in while False | missing | pass |
| Registry dispatch only in a false branch | missing | pass |
| Registry call only inside an uncalled helper | missing | pass |
| Direct registry dispatch in loop | accepted | pass |
| Bare invocation of async def | missing | pass |
| Bare reference without call | missing | pass |

This was a reconstructed local harness, not execution of the committed repository file or the full npm run all suite.

Hosted CI run 40425726921 targeted exact head e30885ef4c228d9a85648cdd05794b570e3f8233 but failed with no step summaries. It is an execution-environment blocker, not evidence that tests passed or that source tests failed. No full suite, deployment, or production behavior has been verified on this head.

## Great Scale mapping

Separate four predicates for each required invariant P on revision R:

- S(P): the requirement is specified.
- Reach(P,C): the canonical command graph C can reach a valid test for P.
- Exec(P,R): that test body actually executes against revision R.
- Obs(P,R): the result and exact tested revision are observed and recorded.

Then a defensible verification claim requires:

\[
Verified(P,R) = S(P)\land Reach(P,C)\land Exec(P,R)\land Obs(P,R)
\]

The AST auditor can provide evidence about Reach, within its supported syntax. It cannot independently establish Exec or Obs. Those require an executed test process with exit status and revision-bound run evidence.

## Success criteria and remaining gates

1. The committed manifest-audit tests pass on a clean checkout of the exact head.
2. npm run all executes all required modules, reports a nonzero exit for a failing test, and finishes successfully only when each command succeeds.
3. Hosted execution records the exact head SHA and real step results; zero-step or runner_id=0 runs are classified as unavailable evidence.
4. Unsupported async or control-flow patterns fail closed until their runner semantics are explicitly modeled and tested.
5. PR #128 remains draft and unmerged until these gates are satisfied.

## Profound conclusion

Verification is not a property of the existence of a test file or even of a plausible AST path. It is a property of the complete chain from invariant, through reachable test, to actual execution, to an observable result bound to the reviewed revision. A verifier must itself be tested adversarially, because an unsound verifier can turn missing evidence into a false success.
