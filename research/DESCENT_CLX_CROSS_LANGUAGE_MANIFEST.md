# Descent CLX — Verification manifests must cover every test language

## Finding

The CLIX audit closes a shell-control-flow gap for the Python portion of `npm run all`, but a second blind spot remains: CLVIII's discovered set contains only top-level `test_*.py` files. The repository also has a separate Node test command in `package.json`. A newly added `test_new.js`, `test_new.cjs`, or `test_new.mjs` could be omitted from `scripts.test` while the Python-only manifest check still passes.

This is a scope error in the verifier: complete coverage within one language is not complete coverage of the repository's declared test surface.

## Formal contract

Let (T_P) be discovered top-level Python test modules, (T_N) discovered top-level Node test entrypoints, (R_P(C_{all})) the Python targets in the aggregate, and (R_N(C_{test})) the Node targets in `npm test).

Require:

[
T_P \subseteq R_P(C_{all})
\quad\land\quad
T_N \subseteq R_N(C_{test})
\]

Also require all referenced targets to exist and both command strings to use the audited, fail-closed grammar. These are reachability constraints, not proof that the test assertions are correct.

## Integrated regression

Added `test_great_scale_clx_cross_language_manifest.py` and wired it into `npm run all`. It checks the actual Node test command, detects an omitted JavaScript test, and rejects a success fallback that could mask a failed Node test.

## Verification boundary

The remote Git tree at the inspected candidate contains three top-level Node test entrypoints and twenty-one top-level Python test modules. The aggregate command references twenty-one Python test modules, and `npm test` references the three discovered Node entrypoints. These are source-tree comparisons; they do not establish that the suites ran successfully. A clean checkout and qualifying hosted Actions result remain necessary.

## Great Scale interpretation

The verification dependency graph is multi-language. A proof of completeness over (T_P) says nothing about (T_N). Repository-wide verification requires the union of all declared test surfaces, with execution semantics constrained so textual references cannot masquerade as reachable tests.
