# great_scale.py v1.2.0 — API surface (local authoritative)

Full source lives in the observer harness (artifacts/great_scale_observer/great_scale.py).
Pushed summary for federation; runtime remains local until LICP bridge sync.

## Constants
- PHI, PHI_INV, PHI_INV2, CONE = φ^{-3} ≈ 0.236068 (authoritative)
- RESIDUAL_ALPHA = 0.1
- VERSION = "1.2.0"
- RESIDUAL_DIMS = [4, 3, 1]

## New functions
```python
def residual_compose(a: float, b: float, alpha: float = RESIDUAL_ALPHA) -> float:
    """alpha*I + (1-alpha)*(a*b) — prevents rank-1 collapse."""

def orientation_entropy(signs: List[float]) -> float:
    """Binary Shannon orientation diagnostic [0,1]."""
```

## coherent_geometry() additions
- residual_composition, capability_hooks, control_lattice
- cone.identity = "φ^{-3} = φ^{-1} - φ^{-2} = √5 − 2"
- version / gs_ucl = "1.2"

## Laws (unchanged + residual composition)
Keep mean · residual 4+3+1 · Ψ ≥ CONE · scale-generated only · residual composition retains variance
