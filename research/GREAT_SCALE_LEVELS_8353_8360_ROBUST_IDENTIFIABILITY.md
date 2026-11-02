# Great Scale Descent — Levels 8353–8360
## Robust distinguishability under bounded observation noise

**Status:** exact finite-dimensional mathematical result plus deterministic regression. Not a physical claim.
**Predecessors:** Levels 8337–8344 (lossy observation) and 8345–8352 (sign certification).
**Question:** when do two latent states remain distinguishable after both projection and bounded measurement error?

## 1. Observation geometry

Let a state x be mapped to an observation F(x) in a normed vector space. The measured observation is y = F(x) + e, where the error satisfies ||e|| ≤ ε.

For a candidate state x, the set of observations allowed by this bound is the closed ball B(F(x), ε). Two states x₁ and x₂ are robustly distinguishable under this error model when their allowed observation balls do not intersect. In a normed space, a sufficient and (for ordinary norm balls) exact condition for disjoint closed balls is:

||F(x₁) − F(x₂)|| > 2ε.

If the distance is ≤ 2ε, the balls intersect or touch, so there exists at least one observation compatible with both states. No classifier using only y and this bound can guarantee correct distinction for every admissible error in that overlap.

This is a worst-case guarantee. Statistical separability under a specified noise distribution is a different question and requires a probabilistic model.

## 2. Projection and noise are different failure modes

If F(x₁) = F(x₂), then the distance is zero: the states are not identifiable even at ε = 0. Better precision cannot repair this collision. Adding a channel may make the mapped observations differ, but if the resulting separation is at most 2ε, the distinction is still not robust to the stated bounded error.

Thus there are two sequential gates:
1. **Structural identifiability:** F(x₁) ≠ F(x₂) for the states to be distinguished.
2. **Robust identifiability:** ||F(x₁) − F(x₂)|| > 2ε under the declared norm and error bound.

Neither gate proves that the forward model F describes a real experiment correctly.

## 3. Simple example

Suppose two augmented observations are F(x₁) = (0, 0, +1) and F(x₂) = (0, 0, −1). Their Euclidean distance is 2. With ε = 0.4, the error balls are disjoint because 2 > 0.8. With ε = 1, they touch; worst-case guaranteed distinction is lost. If the signed channel is dropped, both become (0,0), and they collide even with zero error.

## 4. Great Scale mapping

| Level | Operation | Mathematics/science visible | Evidence |
|---|---|---|---|
| 8353 | Define forward map F and norm | State precisely what is observed | Model and units |
| 8354 | Define bounded error ε | Separate resolution from structural information | Defensible error envelope |
| 8355 | Compute pairwise separation d = ||F(x₁)−F(x₂)|| | Quantify distinguishability | Reproducible calculation |
| 8356 | Compare d with 2ε | Establish worst-case robust separation | Strict inequality test |
| 8357 | Detect projection collision d = 0 | Identify irrecoverable information loss | Counterexample |
| 8358 | Add independent signed channel | Test whether the collision is removed | Channel-ablation test |
| 8359 | Stress-test error boundary | Validate d just below, at, and above 2ε | Boundary regression |
| 8360 | Gate scientific claims | Keep model validity separate from mathematical separability | Provenance and model checks |

## 5. Profound finding

**Identifiability is not a single yes/no property once measurement error is admitted. It has a structural layer and a robustness margin.** A channel can restore structural identifiability without restoring robust identifiability. The separation margin d − 2ε is the relevant worst-case quantity: positive means disjoint error balls; zero or negative means no universal guarantee under this model.

This extends the prior signed-interval rule to vector observations. It is an exact geometric statement conditional on the declared norm and valid error bound—not proof of quantum behavior, a physical topology, or the calibration of an instrument.

## 6. Acceptance boundary

A result may be labeled **structurally distinguishable** when the modeled observations differ; **robustly distinguishable under ε** only when d > 2ε; otherwise label it **unresolved under the declared error model**. If ε is absent or unvalidated, robust certification is unavailable.
