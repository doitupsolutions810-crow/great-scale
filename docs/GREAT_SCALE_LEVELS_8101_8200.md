# Great Scale — Levels 8101–8200: residuals must respect the geometry of the state space

## Finding

The declared involution is defined on a ninefold circle, where (x) and (x+9) represent the same point. The implementation used the ordinary real-line difference
[
R_{\mathbb R}(x)=|x-f(x)|.
]
That quantity is not invariant under the circle's equivalence relation. For example, (0\sim9) and (f(0)=f(9)=0), but (R_{\mathbb R}(0)=0) while (R_{\mathbb R}(9)=9). The residual therefore assigned different “stress” to two representatives of the same circle point.

This is a concrete mathematical inconsistency between the stated circular state space and the residual metric. It is not a physical observation or a quantum-geometry result.

## Integration

- Changed the ES-module and CommonJS implementations to use the existing circular metric: `stressResidual(x) = modDist(x, involution(x))`.
- Changed the Python reference `stress_residual` to use `mod_dist`.
- Added JavaScript and Python regressions requiring zero residual at the identified boundary (0\sim9), and periodicity under (x\mapsto x+9).
- Updated the README and the model hypothesis wording to identify the residual as a circular distance.
- Preserved the involution and contraction definitions; this change repairs the metric used to measure the point-to-image separation.

## Mathematics

Let the state space be the quotient circle
[
S^1_9=\mathbb R/(9\mathbb Z),
]
with equivalence (x\sim y\iff x-y\in9\mathbb Z). Its shortest-arc distance is
[
d_9(x,y)=\min(r,9-r),\quad
r=((x-y)\bmod9)\in[0,9).
]
For the involution (f(x)=(-x)\bmod9), define
[
R(x)=d_9(x,f(x)).
]
Then the residual is representative-invariant:
[
R(x+9k)=R(x)\quad\text{for all }k\in\mathbb Z.
]
In particular, (R(0)=R(9)=0), because these are the same circle point and both map to the same point.

The former real-line residual does not satisfy this condition:
[
|9-f(9)|=9\ne0=|0-f(0)|.
]

## Science and engineering interpretation

A metric is part of the model, not just a display choice. When the state space identifies representatives, all reported distances and residuals must descend to the quotient: their values must be invariant under the equivalence relation. Otherwise a monitor can report a nonzero discrepancy caused only by the choice of coordinate representative.

This is a mathematical/software consistency result. It does not establish that the chosen circle model describes a physical system, and it does not validate any quantum-geometry hypothesis.

## Great Scale mapping

| Level | Mathematics | Science / engineering meaning | Test / verification gate |
|---|---|---|---|
| 8101 | (x\sim x+9k) | Coordinates are representatives of one circle point | Boundary-equivalence tests |
| 8110 | (d_9(x,y)=\min(r,9-r)) | Use shortest-arc distance, not real-line distance | Compare boundary and interior values |
| 8120 | (R(x)=d_9(x,f(x))) | Residual must respect the model's geometry | JavaScript/CJS/Python implementation alignment |
| 8130 | (R(x+9k)=R(x)) | Equivalent representations must yield the same monitor value | Periodicity regressions for (x\to x+9) |
| 8140 | (\text{metric consistency}\ne\text{physical validation}) | Correct internal geometry is necessary but not empirical evidence | Keep software and physical claims separately labelled |

## Test / verify / run / build status

- **Source integration:** ES-module, CommonJS, Python reference, README, and test sources were updated and fetched back from GitHub to confirm the intended edits.
- **Regression source:** boundary-equivalence and periodicity cases are present in JavaScript and Python test files.
- **Repository execution:** not verified in this session. No claim is made that `npm test`, `python3 test_descent.py`, or `npm run all` passed.
- **CI:** latest inspected workflow run `39874200685` was marked failed with no step summaries, usable logs, or artifacts; the root cause is unknown.
- **Branch state:** latest comparison reported 158 commits ahead and 2 behind `main`; branch head may advance as parallel research commits land, so re-check before promotion.
- **Promotion:** keep PR #89 draft/unmerged until exact-head tests execute with inspectable logs and a validated same-run receipt.

## Conclusion

**The profound finding is that a residual is only meaningful if it is invariant under the representation equivalences of the space it measures.** Great Scale's circular state model therefore requires a circular residual metric; a real-line difference silently breaks the quotient geometry.
