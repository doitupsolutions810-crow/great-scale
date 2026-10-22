# Great Scale — Levels 7801–7900: cross-module contract equivalence

## Finding

The public ES-module implementation (`public/scale.js`) and its CommonJS mirror (`public/scale.cjs`) had drifted despite representing the same Great Scale model.

Source inspection found three concrete inconsistencies:

1. The ES module exposed `RESIDUAL_DIMS`, `CONE_MATRIX`, and `FIB_MATRIX`, while the CommonJS export omitted them.
2. The ES module reported `great-scale.descent/v0.5.1`, while the CommonJS snapshot reported `great-scale.descent/v0.5.0`.
3. The two `HYPOTHESIS` arrays differed in wording and the ES module included a matrix-related statement absent from CommonJS.

The main test entry point imported the CommonJS mirror, so a passing `npm test` alone did not prove that the ES-module public API matched it. This is a reproducibility and interface-consistency defect, not evidence that the underlying mathematical recurrence is false or that a deployed consumer was affected.

## Integration

- Aligned the CommonJS mirror's release identity with v0.5.1.
- Added the missing constants and matrices to the CommonJS exports.
- Aligned the hypothesis statements across module formats.
- Expanded the ES-module default export to expose the same keys as the CommonJS API.
- Added `test_scale_module_parity.js`, which imports the exact ES-module source through a data URL and compares API keys, constants, matrices, hypothesis statements, representative dynamics, state outputs, and descent-engine snapshots.
- Added the parity test to the canonical `npm test` script.

## Mathematics

Let (F_E) and (F_C) denote the ES-module and CommonJS realizations of the same declared model, and let (mathcal X) be the tested input set. Behavioral parity requires

\[
\forall x\in\mathcal X,\quad F_E(x)=F_C(x),
\]

together with contract parity:

\[
\operatorname{API}(F_E)=\operatorname{API}(F_C),\qquad
\operatorname{constants}(F_E)=\operatorname{constants}(F_C),
\]

and matching versioned state identifiers. The finite regression set is evidence for the tested cases, not a mathematical proof of equivalence for all possible inputs. A stronger assurance strategy would generate both module formats from one canonical source or prove the transformation preserves semantics.

For the core scalar recurrence,

\[
x_{n+1}=x_*+k(x_n-x_*),\qquad x_*=4.5,
\]

the error satisfies

\[
|x_n-x_*|=|k|^n|x_0-x_*|,
\]

so convergence follows for (|k|<1). That theorem is unchanged by the packaging drift; the engineering issue is ensuring both shipped module surfaces implement and identify the same model.

## Science and engineering interpretation

This is a reproducibility finding: a model is not a single executable object when consumers can load different module formats with different constants, metadata, or hypotheses. Mathematical correctness of one implementation does not establish implementation equivalence across packaging boundaries.

The matrix identities and contraction recurrence remain deterministic mathematical claims about the declared model. They do not establish empirical physical truth or a new quantum-geometry law.

## Great Scale mapping

| Level | Mathematics | Science / engineering meaning | Required gate |
|---|---|---|---|
| 7801 | (\operatorname{API}(F_E)=\operatorname{API}(F_C)) | Public module surfaces must agree | Compare named and default export keys |
| 7810 | (CONE_{E}=CONE_{C}), (M_E=M_C) | Constants and matrix data cannot silently drift | Deep equality of constants and matrices |
| 7820 | (HYPOTHESIS_E=HYPOTHESIS_C) | Declared model claims must be version-consistent | Exact hypothesis-array comparison |
| 7830 | (F_E(x)=F_C(x)) for regression inputs | Both module formats should produce matching dynamics | Compare involution, contraction, and state outputs |
| 7840 | (version_E=version_C) | Receipts and snapshots must identify the same model version | Snapshot parity test |
| 7850 | Tested parity (
e) universal proof | Regression success is bounded evidence | Keep finite-test and formal-proof claims separate |

## Test / verify / run / build status

- **Source integration:** committed to the research branch; current source commits include the CommonJS alignment, ES default API alignment, parity regression, and canonical test-script update.
- **Test added:** `test_scale_module_parity.js` is wired into `npm test`.
- **Static verification:** source review confirms the three missing constants/matrices are now exported by CommonJS, both module surfaces target v0.5.1, the matrix hypothesis statement is present, and the parity test is in the package test command.
- **Repository test run:** not yet verified. No claim that `npm test` passed.
- **Build:** not run/verified.
- **CI:** must be checked against the exact latest commit; a failure without inspectable job steps/logs cannot be classified as an assertion failure.
- **Promotion:** keep PR #89 draft and unmerged until exact-head test execution and logs are available, a same-run receipt is validated, and the branch's two commits behind `main` are reconciled.

## Boundary

This level closes a concrete source-level interface mismatch and adds a regression path. It does not certify the repository as production-safe, authenticate its CI evidence, or validate the model as empirical physics.
