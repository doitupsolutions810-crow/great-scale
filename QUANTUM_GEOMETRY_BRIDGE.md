# Quantum Geometry Bridge — Great Scale

Status: additive mathematical bridge; not an empirical claim.

## Convention

For a smooth pure-state family, define
[
Q_{mu
u}=langlepartial_mupsi|(I-|psianglelanglepsi|)|partial_
upsiangle,
quad g=operatorname{Re}Q,
quad F_{12}=2operatorname{Im}Q_{12}.
]
For two nondegenerate parameter directions, QGT positivity gives
[
det Q=det g-rac{F_{12}^2}{4}geq0.
]
Define the dimensionless curvature fraction
[
chi=rac{|F_{12}|}{2sqrt{det g}},quad 0leqchileq1.
]
Then the normalized QGT residual is
[
R=rac{det Q}{det g}=1-chi^2.
]

## Exact Great Scale embedding

Set
[
h_Q=rac{1+chi}{2}.
]
Using the existing Great Scale law (operatorname{heat}(h)=h(1-h)),
[
S_Q=operatorname{heat}(h_Q)=rac{1-chi^2}{4}
=rac{1}{4}rac{det Q}{det g}.
]
The existing cone law can be reused without altering the original phase-driven state:
[
Psi_Q=mathrm{CONE}+S_Q,qquad mathrm{CONE}=phi^{-2}.
]
This preserves (0leq S_Qleq1/4) and (Psi_Qgeqmathrm{CONE}).
Saturated geometry ((R=0)) maps to zero geometric heat; zero curvature with a nondegenerate metric ((R=1)) maps to maximal heat (1/4).

## Interpretation, information loss, and limits

- (chi) is dimensionless and measures curvature relative to the metric-area bound.
- (R) is the normalized Gram-determinant residual; (S_Q=R/4) is an exact encoding, not a new physical law.
- The mapping is invariant under simultaneous scaling (gmapsto c g), (Fmapsto cF) for (c>0). It therefore deliberately discards absolute metric scale.
- Because it uses (|F|), the scalar channel also discards curvature sign and orientation; because it uses only a determinant ratio, it does not preserve the full metric anisotropy.
- The bridge is defined only for a positive-definite two-direction metric ((g_{11}>0), (g_{22}>0), (det g>0)); degenerate directions need separate treatment.
- Inputs violating (|F_{12}|leq2sqrt{det g}) are rejected, except for configured floating-point tolerance.
- (S_Q) is a new derived channel. It does not replace the original phase-based (h,S,Psi), or the ninefold involution.
- No material-specific prediction or experimental validation is claimed.

## Verification

Run `npm test` and `python3 test_descent.py`.
The bridge suite covers zero curvature, saturation, intermediate curvature, scale invariance, invalid curvature, degenerate metrics, and non-positive metric diagonals.
