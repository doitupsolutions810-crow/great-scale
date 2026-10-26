# Descent CLIX — A manifest is not reachability unless execution semantics are constrained

## Finding

CLVIII's manifest audit extracted Python command targets using a regular expression. That proves only that filenames occur in certain textual positions; it does not prove that the shell will execute those commands. For example:

```sh
npm test && python3 test_alpha.py || true
```

The test command is textually present, but if it fails, the `|| true` fallback can make the aggregate succeed. Likewise, a command after a false `&&` segment is textually present but unreachable. A filename-only audit can therefore report complete coverage while shell control flow defeats the intended success criterion.

## Formal model

Let (R(C)) be the test files textually referenced by command (C), and (X(C,omega)) be the files actually executed under shell outcome (omega). In general:

[
R(C) \not\subseteq X(C,\omega)
]

The CLVIII invariant (T \subseteq R(C)) is necessary but not sufficient. A stronger practical contract is:

[
T \subseteq X(C,\omega)
\quad\text{for every successful execution }\omega
]

Rather than attempting to implement a complete POSIX shell parser, the CLIX audit adopts a small fail-closed grammar: the aggregate may contain `npm test` and direct `python3 test_*.py` commands joined only by `&&`. Any other segment is rejected for review.

## Integrated regression

Added `test_great_scale_clix_shell_manifest_safety.py` with four checks: validate the actual aggregate, reject an `|| true` fallback, reject a false short-circuit segment, and retain detection of omitted/missing files. The test is wired into `npm run all`.

## Limits

This is intentionally a restricted grammar, not a general shell interpreter. It does not prove the internal semantics of `npm test`, imported test helpers, runtime dependencies, or correctness of the tests themselves. A clean checkout and hosted Actions run remain separate verification obligations.

## Great Scale interpretation

The manifest is a dependency graph, but shell control flow determines which nodes execute. A proof of textual inclusion is not a proof of execution reachability. Restricting the aggregate to a small command grammar makes that gap explicit and reviewable.
