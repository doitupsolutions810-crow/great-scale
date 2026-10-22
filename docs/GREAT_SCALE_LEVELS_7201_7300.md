# Great Scale — Levels 7201–7300: cross-runtime circular invariants

## Profound finding

The previous circular-residual correction updated the JavaScript ES module and its CommonJS mirror, but the Python descent runner still used ordinary line distance:

\[
R_{JS}(x)=R_{CJS}(x)=d_9(x,f(x)),\qquad
R_{Python}(x)=|x-f(x)|.
\]

The package script `npm run all` executes both `node test.js` and `python3 test_descent.py`. Consequently, the project could test two different definitions of the same stress residual. The Python tests checked only that the residual was zero at 4.5 and positive at 2; those assertions do not distinguish the circular metric from the old line metric. The README also retained the old formula.

A second semantic ambiguity was found in the fixed-point description. The map is a reflection on the ninefold circle, not merely a real-line contraction centered at 4.5.

## Mathematical correction

The involution is

\[
f(x)=(9-(x\bmod9))\bmod9.
\]

A circle fixed point satisfies \(f(x)\equiv x\pmod9\), hence

\[
2x\equiv0\pmod9
\quad\Longrightarrow\quad
x\equiv0\text{ or }4.5\pmod9.
\]

Thus the complete fixed set on representatives \([0,9)\) is \(\{0,4.5\}\). The separate contraction

\[
C_k(x)=4.5+k(x-4.5),\qquad |k|<1
\]

has contraction target 4.5. The API name `fixedPoint()` denotes that contraction target; it does not enumerate the involution's full fixed set. A new `involutionFixedPoints()` helper makes this distinction explicit.

Define the circular metric and residual by

\[
d_9(a,b)=\min(r,9-r),\quad
r=((a-b)\bmod9+9)\bmod9,\quad
R(x)=d_9(x,f(x)).
\]

Then \(R(x+9)=R(x)\), and \(R(x)=0\) exactly at the circle fixed points \(x\equiv0,4.5\pmod9\). Representative checks are \(R(0)=0\), \(R(1)=2\), \(R(2)=4\), \(R(4)=1\), \(R(4.5)=0\), \(R(8)=2\), and \(R(9)=0\).

## Integration performed

- Updated `test_descent.py` to use `mod_dist(x, involution(x))`, matching both JavaScript runtimes.
- Added Python checks for the two fixed points, residual values, and periodicity.
- Added `involutionFixedPoints()` to `public/scale.js` and `public/scale.cjs`.
- Clarified in runtime comments and hypothesis text that 4.5 is the contraction target, while the circle involution has fixed points 0 and 4.5.
- Expanded `test.js` to test the complete fixed set and zero residual at both points.
- Updated the README to remove the obsolete line-distance formula.

## Great Scale level map

| Level | Invariant | Interpretation | Regression |
|---|---|---|---|
| 7201 | \(f(x)\equiv-x\pmod9\) | Circle reflection | Modular involution identity |
| 7210 | \(2x\equiv0\pmod9\) | Complete circle fixed set is \(\{0,4.5\}\) | Enumerate and verify both points |
| 7220 | \(R(x)=d_9(x,f(x))\) in JS, CJS, and Python | One mathematical definition across runtimes | Exact sample values in both test suites |
| 7230 | \(R(x+9)=R(x)\) | Residual respects circular equivalence | Period-shift regression |
| 7240 | \(C_k(x)\to4.5\), \(|k|<1\) | Contraction target is distinct from the full fixed set of \(f\) | Existing multi-start descent tests |
| 7300 | Source, docs, and tests agree | No stale residual formula in documented interfaces | `npm run all` on exact PR head |

## Verification record and limits

- **Source analysis:** confirmed the Python residual used line distance while JS/CJS used circular distance.
- **Integrated patch:** all five files updated on branch `research/cross-runtime-circle-invariants`; README and this level map added/updated.
- **Remote source read-back:** all six changed files were read from `research/cross-runtime-circle-invariants` after integration. A follow-up read caught and corrected an interval-boundary mistake in the Python fixed-set regression (`[0,9)` must exclude the duplicate representative 9).
- **Targeted local checks:** 20 reconstructed Python descent assertions and 32 targeted JavaScript invariant assertions passed. Python syntax compilation also passed. These are focused formula checks, not a full run of the repository's exact files.
- **Local full repository run:** not available in this environment; outbound GitHub clone failed because the host could not be resolved. Do not interpret that as a test failure.
- **Hosted CI:** exact-head status shows CodeRabbit success and Vercel deployment failure due to the daily deployment quota (`api-deployments-free-per-day`). No PR-triggered GitHub Actions runs were returned. This is not a passing test/build result and does not show that assertions failed.
- **Scientific scope:** this establishes mathematical consistency of the software model only. It does not validate a physical or quantum hypothesis.

## Conclusion

A mathematical invariant must remain invariant across every runtime that claims to implement it. The circular metric is now the shared intended definition, and the two fixed points of the circle reflection are distinguished from the single target of the continuous contraction. Keep this change unmerged until exact-head automated checks are inspectable.
