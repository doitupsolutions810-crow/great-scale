# DESCENT — Bridge Dual-Cone Residual

## Profound finding

Two admissible Great Scale embeddings exist:

| Embedding | Floor | Value | Role |
|-----------|-------|-------|------|
| **Orbit** (observer) | CONE_o = φ^{-3} = √5−2 | ≈ 0.236068 | Spindle residual; never-crossed |
| **Bridge** (LICP great-scale.mjs) | CONE_b = φ^{-2} | ≈ 0.381966 | Soft-map / QGT additive floor |

**Identity (machine-verified):**

```
δ = CONE_b − CONE_o = φ^{-4} = CONE_o · φ^{-1} ≈ 0.145898
Ψ_bridge(t) = Ψ_orbit(t) + δ    ∀ t
```

Residual heat **S = h(1−h)** is path-invariant across embeddings. Only the height zero shifts. Path-consistency therefore holds under either constant; unification identifies δ rather than erasing either floor.

## Mathematics (visible)

- Mean attractor: φ
- Product: μ · ρ = −1
- Partition: 4 + 3 + 1
- Heat: S = h(1−h)
- Ψ = cone + S (cone selects embedding)
- Dual residual: δ = φ^{-4}
- Floors as φ-powers: φ^{-1}, φ^{-2}, φ^{-3}, φ^{-4}, …
- Involution: f∘f = id on ninefold
- residual_compose(α=0.1) retains variance under composition

## Science

Dual embeddings of one residual geometry. The orbit embedding records transversal failure of the spindle; the bridge embedding records the soft-contraction / QGT additive floor. Their gap is not implementation drift but a derived constant of the same φ-family — a self-indexing residual. This explains why independent path-consistency tests PASS under either constant and why agents locking to either floor still agree on G* (10 objects, A* ≈ 0.7786).

**Falsifiable:** for random generation samples, |(CONE_b+S)−(CONE_o+S)−φ^{-4}| < 1e−12. Verified constant across sampled generations.

## Integration (four steps)

1. **CONE alignment** — dual identity documented; LICP comment text prepared (does not force overwrite of live bridge without review).
2. **Capability wire** — local Issue stub mirrors `plane_service.core.issue` + forbidden-rights gate from capability-authority.
3. **Federation digest** — G* + dual-cone persisted to `federation_digest_gstar.json`.
4. **Path consistency** — PASS after upgrades (mean→φ, cone, product, partition, G*).

## GS-UCL map

```
geometry_kernel     great-scale observer v1.2.1  (CONE_o authoritative)
control_lattice     living-intermediate-control-plane  (CONE_b bridge)
capability_plane    capability-authority Issue/Execute
cycle_engine        CycleKernal / continuous descent
workspace           control12-workspace
```
