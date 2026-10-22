# Great Scale — Levels 7101–7200: circular metric consistency

## Profound finding

The model defines the discrete involution on the ninefold circle:
\[
f(x)=(9-(x\bmod 9))\bmod 9,
\]
and defines \(0\equiv9\) as the same point on that circle. It also provides a circular metric \(\operatorname{modDist}\). However, both runtime mirrors previously implemented the stress residual as ordinary Euclidean distance on the real line:
\[
R_{\rm old}(x)=|x-f(x)|.
\]
That contradicts the declared circle geometry. For example, \(0\) and \(9\) are equivalent on the circle, but \(R_{\rm old}(0)=0\) and \(R_{\rm old}(9)=9\). For \(x=1\), \(f(1)=8\): ordinary distance is \(7\), but the shortest circular distance is \(2\).

## Corrected invariant

Define:
\[
d_9(a,b)=\min\left(r,9-r\right),\qquad
r=((a-b)\bmod9+9)\bmod9.
\]
Then the geometry-consistent residual is:
\[
\boxed{R(x)=d_9(x,f(x)).}
\]

This yields:
- \(R(x+9)=R(x)\) for every real \(x\);
- \(R(0)=R(9)=0\);
- \(R(1)=R(8)=2\);
- \(R(4)=R(5)=1\);
- \(R(4.5)=0\), because \(4.5\) is a fixed point of the reflection on the circle.

The residual measures the shortest separation between a state and its involution image. It is not, by itself, a physical observable or evidence of a quantum effect.

## Integrated code change

Branch: \`research/circular-stress-residual-fix\`

Updated both implementations:
- \`public/scale.js\` (ES module)
- \`public/scale.cjs\` (CommonJS mirror used by the repository test runner)

Both now compute \`stressResidual(x)\` using the existing \`modDist(x, involution(x))\`. The hypothesis text now describes the residual as circular distance rather than ordinary \(|x-f(x)|\).

Added regression coverage to \`test.js\` for:
- boundary equivalence \(R(0)=R(9)=0\);
- representative involution pairs;
- periodicity across positive and negative periods \(R(x)=R(x\pm9)\).

## Great Scale level map

| Level | Invariant | Meaning | Verification |
|---|---|---|---|
| 7101 | \(f(f(x))\equiv x\pmod9\) | Involution is well-defined on the circle | Existing modular identity test |
| 7110 | \(d_9(a,b)=d_9(a+9,b)\) | Metric respects equivalence classes | Boundary and periodicity regressions |
| 7120 | \(R(x)=d_9(x,f(x))\) | Residual uses the same geometry as the map | Explicit values for \(x=0,1,4,4.5,5,8,9\) |
| 7130 | \(R(x+9)=R(x)\) | Equivalent representatives produce equal observables | Positive/negative period test |
| 7140 | \(R(4.5)=0\) | Fixed point has zero residual | Existing fixed-point regression |
| 7200 | Source, mirror, and test agree | No implementation drift between ESM and CJS | Run \`npm test\` and \`npm run all\` on the exact PR head |

## Verification status

- **Source analysis:** confirmed the old residual contradicted the model's declared circle metric.
- **Patch integrated:** both runtime mirrors and regression tests updated on a dedicated research branch.
- **Remote read-back:** must be checked after commit before declaring the artifact verified.
- **Local repository test/build:** not run in this review environment.
- **Hosted CI:** pending PR checks; a commit or green documentation workflow is not equivalent to passing \`npm test\`.
- **Scientific scope:** this is a software/mathematical consistency correction, not experimental validation of Great Scale's broader hypotheses.

## Conclusion

A geometric quantity must respect the equivalence relation of its declared space. The stress residual now uses the circular metric already present in the implementation, eliminating the seam inconsistency at \(0\equiv9\) and making the residual periodic. The fix remains unmerged until exact-head tests and review complete.
