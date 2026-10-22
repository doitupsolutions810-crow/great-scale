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

## Run

```bash
npm test
python3 test_descent.py
npm run all
```

## Provisional log-loss certificate

The static viewer includes an optional log-loss interval calculator. It assumes independent groups, repeated Bernoulli trials within each group, and a justified support gap `δ` such that `P ≤ 1 − δ`. It reports separate within-group measurement and between-group sampling radii, plus an optional threshold classification. The support assumption is user-supplied, not inferred from the observations. Because `f(P) = −a ln(1−P)` is increasing in `P`, its meaning and the objective sign must be settled before interpreting the result as a risk or reliability score. This utility is a model-conditional research aid, not a physical measurement or a canonical Great Scale law.

The between-group radius is an uncertainty floor for fixed group count: increasing repeats within each group reduces measurement error but cannot push the total radius below that floor. A requested precision below it requires more independent groups, not merely more repeats. The calculator caps input at 10,000 groups, requires safe-integer trial counts, and rejects parameters that overflow finite numeric results.

For exact population moments `p = E[P]`, `v = Var(P)`, and justified support `0 ≤ P ≤ b = 1−δ`, the viewer computes the **sharp** range of `E[f(P)]` for `f(P) = −a ln(1−P)`. Since `f'''(x)=2a/(1−x)^3>0`, quadratic Hermite interpolation gives an exact lower extremizer on `{0,u}`, where `u=p+v/p`, and an exact upper extremizer on `{l,b}`, where `l=p−v/(b−p)`. The corresponding endpoint distributions preserve both supplied moments; the displayed expectations are attained, not merely conservative estimates. When `v=0`, both endpoints equal `f(p)`. This is the classical two-moment extremal structure made explicit for this loss function and support.

The sharp upper witness places mass `qδ = v/[v+(1−δ−p)²]` at the support boundary. For fixed `0 < p < 1` and `0 < v < p(1−p)`, as `δ → 0`, `qδ → q₀ = v/[v+(1−p)²]` and the sharp upper endpoint obeys `Uδ = C ln(1/δ) + R + o(1)`, where `C = a q₀` and `R = a(1−q₀)[−ln(1−p+v/(1−p))]`. Thus the divergence rate is determined exactly by the variance-constrained extremal boundary mass; zero variance instead gives the finite value `f(p)`. This is a mathematical sensitivity result conditional on fixed exact moments and support, not evidence that a physical system follows this model or that the support assumption is justified. It remains an auxiliary research sidecar, not a new canonical Great Scale level or a continuation of the symmetry/phase result.

For comparison, the viewer also reports valid but generally non-sharp upper bounds: the chord bound `E[f(P)] ≤ a p ln(1/δ)/(1−δ)`, the curvature bound `E[f(P)] ≤ f(p)+a v/(2δ²)`, and the series bound `E[f(P)] ≤ a[p+(p²+v)(ln(1/δ)−(1−δ))/(1−δ)²]`. The sharp interval is conditional on exact moments and justified support; it is not a sampling-confidence interval, and estimated moments need their own uncertainty treatment. As `δ → 0`, the upper endpoint can diverge even when `p` and `v` are held fixed.

## Bounded-disturbance descent certificate

For the scalar descent `x′ = 4.5 + k(x − 4.5) + w`, with `|k| < 1`, `|w| ≤ ε`, and projection back to `[1, 8]` after each step, the stress residual `R = |x − f(x)| = 2|x − 4.5|` satisfies `Rₜ₊ₙ ≤ min(7, |k|ⁿRₜ + 2ε(1−|k|ⁿ)/(1−|k|))`. Therefore `limsup R ≤ min(7, 2ε/(1−|k|))`. The viewer computes this conditional bound; it does not estimate `ε`, and the certificate is not empirical evidence.

Live UI: https://great-scale.vercel.app

See LATTICE_BRIDGE.md for control-plane integration.
