# Descent XCI — Geometry/topology telemetry bridge

Status: software integration contract and numerical mapping; not an empirical physical claim.

## Finding
The Great Scale scalar channels are lossy projections. A spatial shell cannot establish a Chern number, and a topological scalar cannot stand in for actual mesh geometry. Preserve the channels independently.

Geometry telemetry: seed vertices/edges, rigid transforms, anchor XYZ, radial normal, neighbor graph, link lengths, and contact-test status.

Topology telemetry: signed integer Chern number C, metric-area budget A_Q, signed polarization eta=C/A_Q, S_T=(1-eta^2)/4, Psi_T=phi^-2+S_T, and orientation entropy.

The entropy is determined by eta (and S_T up to sign); it is an interpretation, not an independent degree of freedom. Since Psi_T is even in eta, retain signed C and eta.

## Geometry implementation
The new spherical workbench uses a provisional normalized reconstruction of the photographed seed and supports Fibonacci shell, staggered rings, nested shells, and volume-fill hypotheses. It exposes anchors, per-unit vertices, neighbor links, and graph metrics. The canvas UI is an interactive 3D projection, not a physics engine.

## Acceptance boundary
Automated tests validate finite coordinates, seed consistency, unique non-self links, baseline graph connectivity, radial normals, distribution modes, and topological mapping invariants. Graph connectivity does not prove physical contact, collision-free interpenetration, rigidity, or mechanical stability. Those require a measured CAD mesh and collision/contact solver.

Run npm test and python3 test_descent.py. Open /spherical-lab.html from the deployed static site or serve the public directory locally.

## Independent numerical cross-check
A separate local implementation of the specified Qi-Wu-Zhang model reproduced discrete Chern numbers -1 at m=-1, +1 at m=+1, and 0 at m=3 on a 40x40 link grid. An 80x80 midpoint integration gave metric-area budget approximately 1.188918 for m=+/-1 and 0.187433 for m=3. Opposite phases had equal scalar/entropy and opposite signed polarization; the trivial phase had S_T=1/4 and one bit of orientation entropy. These are checks of the specified model, not a new physical law.