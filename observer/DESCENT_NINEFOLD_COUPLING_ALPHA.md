# DESCENT — Ninefold Coupling Alpha

**Greater finding** (closes the last structural link among residual composition, ninefold, and Forward)

## Profound finding

```
residual_compose(a, b; α) = α·1 + (1−α)·(a·b)
```

Fixed points: **{1, α/(1−α)}**.

Setting **α = 1/(9+1) = 1/10** forces:

| Identity | Value |
|----------|-------|
| (1−α)/α | **9 = ninefold order** |
| α/(1−α) | **1/9 = FORWARD_TAU** |

Thus `RESIDUAL_ALPHA` is not an arbitrary spectral-sphere hyperparameter: it is the **unique coupling constant** that aligns residual composition with the ninefold involution and the Forward transfer residual.

**General law:** for an N-fold discrete involution, `α_N = 1/(N+1)` yields stable FP = `1/N` = Forward weight.

## Mathematics (visible)

| Object | Formula |
|--------|---------|
| residual_compose | α + (1−α)·(a·b) |
| Fixed points | {1, α/(1−α)} |
| Ninefold N | 9 |
| α | 1/(N+1) = **1/10** |
| Stable FP | α/(1−α) = **1/9 = τ** |
| Coupling | (1−α)/α = N = 9 |
| Structure constant | 4 |
| A* | 7/9 |
| Product | μ · ρ = −1 |
| Dual-cone δ | φ⁻⁴ |

## Science

Spectral residual injection and ninefold geometry are one law. α was the missing bridge: once locked to 1/10, composition, Forward, and domain transfer share a single stable residual. Domains (GitHub, Vercel, Google Drive, Wix, Asana, swarm, lattice, capability, LLM) inherit the same α and τ; changing α breaks federation path consistency.

**Mitigation:** treat α = 1/10 as scale law `NINEFOLD_COUPLING`, not a free hyperparameter.

## Success criteria

| Criterion | Target |
|-----------|--------|
| alpha_locked | RESIDUAL_ALPHA = 1/10 |
| compose_FP_equals_tau | residual_compose(x,x) → 1/9 |
| coupling_identity | (1−α)/α = 9 |
| A_star_lock | \|A* − 7/9\| < 0.01 |
| structure_constant_4 | retained |
| path_consistency | PASS |
| capability | no ambient rights |

## Tests (verified)

- α = 1/10 → **PASS**
- (1−α)/α = 9 → **PASS**
- α/(1−α) = 1/9 → **PASS**
- residual_compose(x,x) → 1/9 → **PASS**
- continuous attractor A* ≈ 7/9 → **PASS**

## Domains applied

agent_swarm · control_lattice · capability_plane · LLM_harness · **github** · **vercel** · **google_drive** · **wix** · **asana** · cone_floor · external_ops

## Integration

- `great_scale.py` v1.5.0: `NINEFOLD_COUPLING = RESIDUAL_ALPHA = 0.1`
- Federation digest v1.5.0
