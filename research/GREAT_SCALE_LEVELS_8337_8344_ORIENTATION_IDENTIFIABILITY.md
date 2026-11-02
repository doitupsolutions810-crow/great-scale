# Great Scale Descent — Levels 8337–8344
## Orientation is information that scalar coherence cannot recover

**Status:** research proposal + deterministic mathematical regression; not a physical claim.  
**Scope:** connect the minimal-channel/identifiability audit (Descent XCI) to the spherical geometry/topology telemetry lab (PR #111).  
**Evidence boundary:** repository source and PR descriptions motivate the counterexample; the statements below are algebraic and numerically testable. They do not validate a photographed object's physical geometry or establish a physical law.

### 1. Descent question

Can a Great Scale scalar, even when paired with an entropy-like scalar, identify the orientation/topological phase of a system?

The relevant reported QWZ audit has opposite signed Chern phases with equal Great Scale scalar and orientation entropy. If two states differ in a scientifically meaningful signed invariant but all observed channels are equal, the measurement map is not injective.

Let the full state be (x), the reported channels be (F(x)=(G(x),E(x),A(x))), and a signed invariant be (C(x)). Identifiability of (C) from these channels requires
[
F(x_1)=F(x_2)\implies C(x_1)=C(x_2).
]
A counterexample (F(x_+)=F(x_-)) with (C(x_+)=-C(x_-)
e0) disproves that implication. It does **not** disprove the usefulness of (G) or (E); it proves only that they are insufficient for this target.

### 2. Minimal counterexample and remedy

Take the abstract states (x_+=(g,e,+1)) and (x_-=(g,e,-1)), with (g,e) equal in both states. Then the projection (pi(x)=(g,e)) identifies two states whose signed invariant differs. Add a signed channel (C):
[
widetilde F(x)=(G(x),E(x),C(x)).
]
For this pair, (widetilde F(x_+)
ewidetilde F(x_-)). This restores distinguishability for the counterexample, not universal identifiability for arbitrary systems.

**Channel contract:** store the unsigned magnitude/scale, entropy, and signed topological/orientation quantity as separate fields. Never infer the sign of (C) from (G) or (E), and never fold signed (C) into a magnitude-only summary without retaining the original value.

### 3. Great Scale mapping

| Level | Mathematical operation | Scientific interpretation | Required check |
|---|---|---|---|
| 8337 | State (	o) observed channels | Specify exactly what the instrument reports | Channel schema is explicit |
| 8338 | Projection (pi:xmapsto(G,E)) | Information can be discarded by summarization | Construct a collision |
| 8339 | Signed invariant (C(x)) | Orientation/phase can distinguish states | Opposite-sign pair |
| 8340 | Non-identifiability theorem | Equal observations do not imply equal hidden state | Counterexample is executable |
| 8341 | Augmentation ((G,E)mapsto(G,E,C)) | Add the missing independent channel | Pair becomes distinguishable |
| 8342 | Robustness/precision boundary | Numerical estimates can be noisy or undefined | Separate estimate, uncertainty, and status |
| 8343 | Provenance binding | A number is meaningful only with model, grid, convention, and code revision | Metadata accompanies output |
| 8344 | Promotion boundary | A mathematical counterexample is not physical validation | Keep claims and evidence classes separate |

### 4. Exact conclusion

The profound finding is an **observability boundary**:

[
\boxed{\text{A summary can be invariant under a transformation that reverses a scientifically relevant sign.}}
]

Therefore, a scalar can be perfectly reproducible and still be insufficient to identify the state. Better numerical precision cannot recover information removed by a many-to-one projection. The remedy is not to increase precision on the same scalar; it is to preserve an independent signed channel (and its convention/provenance).

This is a general information/identifiability result. Whether the chosen channel is physically valid depends on the model, measurement protocol, discretization, and uncertainty analysis.

### 5. Deterministic regression contract

The companion test checks only the algebraic counterexample:
1. Equal (G) and (E) for the two states.
2. Opposite nonzero (C).
3. The projection ((G,E)) collides.
4. The augmented tuple ((G,E,C)) separates the pair.
5. No code path derives (C) from (G) or (E).

This regression is deliberately not a Chern-number solver. The separate QWZ numerical audit must still check grid refinement, gap closure, sign convention, Berry-curvature integration, and convergence against a trusted implementation.

### 6. Verification ledger

- **Analytic proof:** established for the explicit two-state counterexample above.
- **Companion regression:** intended to make the implication/counterexample executable.
- **Repository test suite / hosted CI:** not claimed until a runner executes the exact commit and exposes step logs.
- **Physical validation:** not established by this note.
- **Promotion rule:** keep as research until the regression, full repository suites, and any numerical QWZ audit run against the exact candidate commit with inspectable evidence.
