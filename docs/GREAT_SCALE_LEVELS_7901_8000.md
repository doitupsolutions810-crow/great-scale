# Great Scale — Levels 7901–8000: executable checks must agree with the declared mathematics

## Finding

A cross-module audit found the canonical test entry point `test.js` contained malformed `require` string literals, including the assertion-library import and both public-module imports. Separately, `public/residual-ops.cjs` had an unterminated import string. These are parse-time failures: Node cannot execute the intended assertions in those files until the syntax is corrected.

The same audit found a mathematically inconsistent assertion in the residual matrix test. The documented matrix is
[
M=\begin{pmatrix}2&-1\\-1&1\end{pmatrix},
]
and direct multiplication gives
[
M^3=\begin{pmatrix}13&-8\\-8&5\end{pmatrix}.
]
The test incorrectly expected the lower-right entry to be (13), contradicting both the expected matrix printed in its test name and the residual-operation module's own SC6 check. The correct entry is (5).

This is a source-level defect finding. The inspected CI run is marked failed but exposes no step details, logs, or artifacts, so it cannot be attributed conclusively to these errors.

## Integration performed

- Repaired the assertion-library import and both public-module imports in `test.js`.
- Repaired the CommonJS import in `public/residual-ops.cjs`.
- Corrected the matrix-power assertion from (M^3_{22}=13) to (M^3_{22}=5).
- Kept the determinant assertion (\det(M^3)=1), consistent with (\det(M)=1).
- No changes were made to the recurrence or matrix definitions; the integration aligns the executable test with the already-declared algebra.

## Mathematics

For
[
M=\begin{pmatrix}2&-1\\-1&1\end{pmatrix},
quad \operatorname{tr}(M)=3,quad \det(M)=1,
]
the characteristic polynomial is
[
p(\lambda)=\lambda^2-3\lambda+1.
]
Multiplying,
[
M^2=\begin{pmatrix}5&-3\\-3&2\end{pmatrix},\qquad
M^3=\begin{pmatrix}13&-8\\-8&5\end{pmatrix}.
]
Therefore
[
\det(M^3)=13\cdot5-(-8)(-8)=65-64=1.
]
The test oracle must agree with the matrix product; otherwise the test rejects the correct implementation.

## Science and engineering interpretation

A verification system has two separate obligations: the checker must be executable, and its expected result must be correct. A syntax-valid test can still encode a false oracle; a correct oracle in an unparseable file never runs. Therefore a test suite's assurance requires at least:
1. syntax/loadability of each test and module,
2. mathematical correctness of expected values,
3. execution on the exact revision,
4. inspectable logs and result artifacts.

These are software verification properties. They do not validate a physical quantum-geometry interpretation.

## Great Scale mapping

| Level | Mathematics | Science / engineering meaning | Test / verification gate |
|---|---|---|---|
| 7901 | (M^3_{22}=5) | The executable oracle must match the matrix product | Corrected assertion in `test.js` |
| 7910 | (det(M^3)=det(M)^3=1) | Independent algebraic cross-check | Determinant assertion retained |
| 7920 | (operatorname{parse}(source)=\text{success}) before execution | Test files and modules must load before their checks can run | Fixed import strings; exact-head syntax/test run still required |
| 7930 | (	ext{declared API}=	ext{loaded API}) | CommonJS dependencies must resolve at runtime | Fixed `residual-ops.cjs` import; module load unverified in repository runner |
| 7940 | (	ext{source review}\ne	ext{execution evidence}) | Static repair does not prove suite success | Require runner steps, logs, and same-run receipt |

## Test / verify / run / build status

- **Source inspection:** confirmed malformed import literals in the canonical test entry point and CommonJS residual module; confirmed the inconsistent matrix expectation.
- **Integration:** fixes are committed on the research branch.
- **Local execution:** unavailable in this session; no local `npm test`, `python3 test_descent.py`, or build success is claimed.
- **CI:** latest inspected run `39874145046` is marked failed, with no step details, logs, or artifacts. Its failure cause is therefore unknown.
- **Branch state:** the research branch is 154 commits ahead and 2 behind `main` at the last comparison. Reconcile divergence before promotion.
- **Promotion:** keep PR #89 draft/unmerged until the exact current SHA has inspectable runner steps, both required suites pass, the receipt artifact is present and validated, and branch divergence is resolved.

## Conclusion

**The profound finding is that verification can fail at two different layers: the test program may not parse, or it may parse but encode the wrong mathematical oracle.** A trustworthy Great Scale result requires both executable verification and internally consistent mathematics, followed by exact-revision execution evidence.
