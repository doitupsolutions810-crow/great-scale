# Great Scale Environment Access

## Geometry version 0.4.0 — phase-time camera atlas

### Laws
- Keep the mean (zero-mode ≈ φ)
- Residual partition 4+3+1
- Ψ never below cone √5−2
- Only add scale-generated geometry

### Phase-time fibration
- Base: phase ∈ [0,1)
- Fiber height: H = S = h(1-h)
- Embedding: xyz = ((1+ε)cos θ, 4S, (1+ε)sin θ)

### Camera atlas (embeddings)
| View | Role |
|------|------|
| Watch | spindle + orbit + sequence |
| Observer | law-bound; mean/partition/cone |
| Forward | phase-time advance |
| Adjacent | ninefold neighborhood |
| Down | inward fold direction |

### Agent / LLM access (local)
- `logs/environment_state.json` — live snapshot
- `logs/visual_scale_geometry.json` — visual state
- `logs/coherent_geometry.json` — full geometry stack
- `logs/agent_env_access.jsonl` — agent witness log
- `logs/ollama_witness.jsonl` — local LLM witness log
- Python: `great_scale_observer/env_access.py`

### UI navigation
- Drag canvas to orbit (azimuth / elevation)
- Phase scrubber for phase-time traversal
- View tabs load atlas presets
- Search bar indexes geometry & laws

### Live app
https://great-scale.vercel.app
