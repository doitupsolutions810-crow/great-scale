# Great Scale v0.4.2

**Test environment — three embeddings of one state.**

## Laws

1. Keep the mean — zero-mode φ anchors every state
2. Respect residual partition 4+3+1
3. Ψ = CONE + S never below CONE = φ⁻² ≈ 0.382
4. Only scale-generated geometry

## Math

- heat(h) = h(1−h) ≡ tension(B) = B(1−B)
- involution f(x) = (9 − (x mod 9)) mod 9 — identity modular, fixed point 4.5, two-cycles 1↔8…
- soft contraction x′ = 4.5 + k(x − 4.5), |k|<1 — converges to fixed point
- softMap g(x) = 9 − x — linear involution shadow
- stress residual |x − f(x)| — computational moment of now

## Quantum geometry bridge (additive)

The optional QGT bridge maps the normalized metric-curvature residual into the existing Great Scale heat law without replacing the phase-driven state:

- `curvatureFraction = |F₁₂| / (2√det(g))`
- `S_quantum = heat((1 + curvatureFraction)/2) = det(Q)/(4 det(g))`
- `Ψ_quantum = CONE + S_quantum ≥ CONE`

See [QUANTUM_GEOMETRY_BRIDGE.md](QUANTUM_GEOMETRY_BRIDGE.md) for the derivation and limits. The bridge rejects degenerate metrics and inputs violating QGT positivity. It is a mathematical embedding, not an empirical claim.

## Run

```bash
npm test
python3 test_descent.py
npm run all
```

`npm test` now includes the quantum-geometry bridge checks.

Live UI: https://great-scale.vercel.app

See LATTICE_BRIDGE.md for control-plane integration.
