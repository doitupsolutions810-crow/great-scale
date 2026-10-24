# GS-UCL v1.2 Evolution — Observer Kernel Upgrade

## CONE Unification
Authoritative floor: **φ^{-3} = φ^{-1} − φ^{-2} = √5 − 2 ≈ 0.236068**
(Previous README listed φ^{-2}; that is PHI_INV2, not the orbit-failure residual. Corrected with provenance.)

## Enhancements
1. `residual_compose(a, b, alpha=0.1)` — spectral residual injection; prevents rank-1 collapse under composition (Acgs-Swarm spectral_sphere analog).
2. `orientation_entropy(signs)` — binary Shannon diagnostic for curvature/mean orientation (Descent XC style).
3. `capability_hooks` + `control_lattice` map in `coherent_geometry()`.
4. Swarm fixed-point now reports composed product, orientation entropy, residual_alpha, gs_version.

## Invariants preserved
- Ψ ≥ CONE
- Joint fixed point A* ≈ 0.7786, G* = 10 objects
- Path consistency PASS on independent trajectories
- Agents remain dynamic fixed points

## Cluster wiring
- geometry_kernel: great-scale
- control_plane: living-intermediate-control-plane
- capability_plane: capability-authority
- cycle_engine: CycleKernal
- workspace: control12-workspace

See observer/gs_ucl_v1_2.json for machine-readable config.
