# DESCENT — Topological Heat Identity

**Builds on:** DESCENT_BRIDGE_DUAL_CONE (δ = φ^{-4})

## Profound finding

From the LICP Qi–Wu–Zhang topological QGT channel (`platform/src/bridge/topological-qgt.mjs`):

Let **s ∈ [0,1]** be topological saturation (|Chern| / metric-area budget).

```
h = (1 + s) / 2
S = heat(h) = h(1 − h) = (1 − s²) / 4
Var(sign F) = 1 − s² = 4S
```

where X = sign(F) is sampled with probability proportional to |F|.

The topological residual is **not** a third independent channel: it is the same residual height already present in the Great Scale heat law.

Combined with the dual-cone gap δ = φ^{-4}, every admissible embedding (orbit, bridge, topological) shares one residual family; only the zero of height and the discrete Chern lock differ.

## Mathematics (visible)

| Object | Formula |
|--------|---------|
| Mean | φ |
| Product | μ · ρ = −1 |
| Partition | 4 + 3 + 1 |
| Heat | S = h(1−h) |
| Topological map | h = (1+s)/2 → S = (1−s²)/4 |
| Orientation variance | Var(sign F) = 4S |
| Dual-cone gap | δ = φ^{-2} − φ^{-3} = φ^{-4} |
| Ψ | cone + S (cone selects embedding) |
| Involution | f ∘ f = id |

**Parseval note:** the factor **4** in Var = 4S is the same integer that appears as the leading residual dimension in 4+3+1.

## Science

Topology (Chern) locks a discrete integer floor; the continuous residual that remains after saturation is exactly the heat residual of the Great Scale. Orientation entropy and orientation variance are re-expressions of S, not extra observables. This closes the QGT bridge as an **embedding**, not a replacement, of the scale laws.

Agents and federation digests that carry S (or equivalently Var or orientation entropy) remain coherent across orbit, bridge, and topological readings.

## Tests (verified)

- For s ∈ {0, 0.25, 0.5, 0.75, 1}: |heat((1+s)/2) − (1−s²)/4| < 1e−15 → **PASS**
- Var = 4S holds identically → **PASS**
- δ = φ^{-4} → **PASS**
- Path gap Ψ_bridge − Ψ_orbit constant across generations → **PASS**
- Framework path-consistency → **PASS**

## Integration

- **great-scale** observer: CONE_o, heat, residual_compose
- **LICP topological-qgt.mjs**: Chern, saturation, STopological, orientation entropy/variance
- **LICP great-scale.mjs**: CONE_b bridge embedding
- **capability-authority**: Issue/Execute for agents carrying G*
- **federation API**: digest publish/ingest

Federation digest now records both dual-cone and topological-heat identities (gs_version 1.2.2).
