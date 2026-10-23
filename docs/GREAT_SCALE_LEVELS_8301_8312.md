# Great Scale — Levels 8301–8312: state sufficiency, hysteresis, and transition parity

## Finding and epistemic status

**Derived result from the source-level transition contract:** the promotion decision is not a function of the current fused score alone. It depends on both the score and the prior promotion state. An adapter that reconstructs the prior state from the current score destroys information and can make demotion unreachable.

**Source observation:** in CycleKernal `backend/ns_fusion.py`, `promote_decision(fused, already_promoted)` demotes an already-promoted colony when `fused < 0.28`. But `apply_fusion()` passes `already_promoted = bool(colony.promoted and fused >= 0.62)`. For a previously promoted colony with fused score below 0.28, that expression is false; the shared decision function therefore returns `hold`, not `demote`. In the same repository's `backend/simulation_core.py`, the simulation path passes the stored `promoted` state directly. The two adapters consequently implement different state-transition semantics.

This is a source-level defect in the current `main` snapshot reviewed here (source blob for `ns_fusion.py`: `ddab888c5e88546a362a793de86796e701ec2ab8`; for `simulation_core.py`: `5bf4dec4db280e3ec968ceb5d7767923f28d0c8a`). It is not evidence that a deployed service was reached or exploited. The existing tracked fix is CycleKernal [issue #3](https://github.com/doitupsolutions810-crow/CycleKernal/issues/3) and draft [PR #4](https://github.com/doitupsolutions810-crow/CycleKernal/pull/4); the fix must still be reviewed and tested against the current base.

## Mathematics

Let the full decision state be
`z=(p,s)`, where `p∈{0,1}` is prior promotion state and `s∈[0,1]` is the fused score. Let thresholds be `d=0.28` and `u=0.62`.

```text
T(p,s) = demote, if p=1 and s<d
         promote, if p=0 and s>=u
         hold, otherwise
```

The score projection `π(p,s)=s` is not sufficient to determine `T`: for any `s<d`,
`T(1,s)=demote` while `T(0,s)=hold`, even though `π(1,s)=π(0,s)=s`.

The wrapper's reconstruction `p' = p ∧ (s≥u)` maps every `(1,s)` with `s<d` to `p'=0`. Thus it erases precisely the historical bit required to trigger demotion. No downstream threshold adjustment can recover that bit after it has been discarded.

**General theorem (derived):** if a transition function depends on state component `q`, an adapter may project to a reduced representation `π(z)` only if the transition is constant on every fiber of `π`: whenever `π(z₁)=π(z₂)`, it must follow that `T(z₁)=T(z₂)`. Here that condition fails. Preserve the full state or prove a valid sufficient-state abstraction before adapting.

## Great Scale mapping

| Level | Mathematics | Science / engineering interpretation | Test / verification gate |
|---|---|---|---|
| 8301 | Decision state is `(p,s)`, not just `s` | Promotion is a hysteretic state machine | Inspect transition inputs |
| 8302 | `T(1,s)=demote` and `T(0,s)=hold` for `s<0.28` | Same score, different correct action due to history | Paired-state counterexample |
| 8303 | `π(p,s)=s` is not transition-sufficient | A scalar telemetry value cannot stand in for full control state | Check constancy over projection fibers |
| 8304 | Wrapper sets `p'=p∧(s≥0.62)` | Low score erases prior promotion state | Source predicate audit |
| 8305 | State-machine and wrapper paths disagree | Different entry points produce different outcomes | Adapter parity test |
| 8306 | Preserve state, then apply thresholds | Decision policy must receive trusted prior state | Regression for previously-promoted low score |
| 8307 | `π(z₁)=π(z₂)⇒T(z₁)=T(z₂)` is the criterion for safe abstraction | Any compressed state needs a sufficiency proof | Property-based fiber test |
| 8308 | Transition receipts record prior state, score, policy version, and result | Auditors can reconstruct why an action occurred | Receipt completeness and deterministic replay |
| 8309 | Confidence/score is not authorization | Numerical suitability and decision authority are separate dimensions | Explicit authorization gate |
| 8310 | Shared transition function + explicit state schema | All adapters must use the same state contract | Cross-entry-point integration test |
| 8311 | Counterexample falsifies score-only decision sufficiency | Small counterexamples can expose systemic semantic drift | Run the deterministic toy assertions |
| 8312 | State sufficiency is a precondition for reproducible verification | A correct formula cannot compensate for lossy state mapping | Exact-head tests and verified receipt |

## Test / verify / run / build

A deterministic toy-model check was run during this analysis (not against the repository runtime):

1. Previously promoted, score 0.10: canonical state-machine result is `demote`; wrapper-reconstructed state result is `hold`.
2. Not previously promoted, score 0.10: canonical result is `hold`.
3. Not previously promoted, score 0.62: canonical result is `promote`.
4. Previously promoted, score 0.28: strict demotion boundary does not demote.
5. Score-only projection fails the fiber-constancy condition at score 0.10.

**Toy assertions: 5/5 passed.** This verifies the counterexample and the stated decision table only. The CycleKernal repository test suite, its five tests in draft PR #4, integration tests, security checks, and deployment build have not been run or verified here. Great Scale hosted CI has previously returned failed jobs without retrievable step logs or artifacts; that is not evidence of an assertion failure and is not a pass.

## Integration decision

- Preserve the finding as a source-backed research/engineering invariant; do not describe it as a physical quantum-geometry result.
- Track the runtime correction in CycleKernal issue #3 / PR #4. The safe correction is to pass the stored promotion state unchanged, then test demotion, promotion, hold, and both threshold boundaries.
- Keep any Great Scale integration documentation-only until exact-head repository tests, integration/security checks, and a same-run verification receipt are available.
- Do not merge or deploy on the basis of toy checks alone.

## Profound finding

**State compression is safe only when it preserves every distinction that can change a future transition.** A scalar may summarize the present while being insufficient to determine the next action. The same rule applies to Great Scale descent coordinates, CycleKernel simulation state, agent approval records, and verification receipts: if history or authority changes the transition, that information must remain explicit in the state model. This is a state-sufficiency theorem for the software transition contract, not a claim about physical quantum coherence.
