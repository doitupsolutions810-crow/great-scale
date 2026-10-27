# Great Scale v0.4.2

**Test environment — three embeddings of one state.**

## Laws

1. Keep the mean — zero-mode φ anchors every state
2. Respect residual partition 4+3+1
3. Ψ = CONE + S never below CONE = φ⁻² ≈ 0.381966
4. Only scale-generated geometry

## Math

- heat(h) = h(1−h) ≡ tension(B) = B(1−B)
- involution f(x) = (9 − (x mod 9)) mod 9 — identity modulo nine
- On the continuous ninefold circle, the fixed classes are 0 ≡ 9 (boundary) and 4.5 (interior); the listed integer two-cycles are 1↔8, 2↔7, 3↔6, 4↔5
- Soft contraction x′ = 4.5 + k(x − 4.5), |k|<1 — converges to 4.5
- softMap g(x) = 9 − x — linear involution shadow
- stress residual |x − f(x)| — computational diagnostic, not a physical observable by itself

## Quantum geometry bridge (additive)

The optional QGT bridge maps the normalized metric-curvature residual into the existing Great Scale heat law without replacing the phase-driven state:

- `curvatureFraction = |F₁₂| / (2√det(g))`
- `S_quantum = heat((1 + curvatureFraction)/2) = det(Q)/(4 det(g))`
- `Ψ_quantum = CONE + S_quantum ≥ CONE`

See [DESCENT_LXXVIII_TOPOLOGICAL_QGT.md](DESCENT_LXXVIII_TOPOLOGICAL_QGT.md) for the separate global Chern-number channel and reproducible two-band test. The bridge rejects non-positive or degenerate metrics and inputs violating QGT positivity. It is a mathematical embedding, not an empirical claim. The next step, [Descent LXXXVIII — curvature-sign variance and cancellation](research/DESCENT_LXXXVIII_CURVATURE_SIGN_VARIANCE.md), derives the global scalar as one quarter of a curvature-orientation variance and adds an explicit cancellation-identity audit. [Descent LXXXIX — orientation blindness and identifiability](research/DESCENT_LXXXIX_ORIENTATION_IDENTIFIABILITY.md) adds signed polarization so the scalar does not erase Chern orientation. [Descent XC — curvature-orientation entropy](research/DESCENT_XC_CURVATURE_ORIENTATION_ENTROPY.md) gives a Shannon-entropy calibration and makes the entropy-consistency residual part of the acceptance gate.

## Run

```bash
npm test
python3 test_descent.py
npm run all
```

`npm test` includes the quantum-geometry bridge checks.

Live UI: https://great-scale.vercel.app

See LATTICE_BRIDGE.md for control-plane integration.


## Cross-repository operation/evidence contract

The proposed shared rules for stable operation IDs, durable intent/receipt evidence, indeterminate outcomes, revision binding, and promotion gates are documented in [Operation and Evidence Contract v1](docs/OPERATION_EVIDENCE_CONTRACT_V1.md). The registry is public-only; the complete account inventory belongs in an access-controlled repository.
