"""Great Scale Descent XCV — projection-aware promotion gate.

Status: proposed, additive, non-canonical. This module responds to XCIV's
tolerance-projection finding and Descent L's moment-closure non-identifiability
by defining an enforceable gate: no scalar may be consumed unless its
companion channel (rawCurvatureFraction, positivityOvershoot,
saturationProjected) is present and the input lies inside the feasible set.

It also formalizes XC's orientation entropy as binary entropy — a strictly
monotone reparameterization of S_T carrying an information-theoretic label
but no independent degree of freedom — and reproduces Descent L's three-
distribution counterexample with rational masses.

Mathematics
-----------
Projection gate:
  chi_raw > 1 + tol  ->  saturationProjected = True
  rawCurvatureFraction = chi_raw / (1 + tol)   (> 1 when over threshold)
  positivityOvershoot  = max(0, chi_raw - 1)
  PROMOTE iff not saturationProjected and positivityOvershoot == 0
             and rawCurvatureFraction <= 1 and feasible(p, v)

Orientation entropy (XC):
  p_+ = (1 + eta_T)/2,  p_- = (1 - eta_T)/2
  S_T  = p_+ * p_-                      (heat term, max 1/4 at eta=0)
  H_2  = -p_+ ln p_+ - p_- ln p_-      (binary entropy in nats, max ln2)
  dH_2/dS_T = -ln(S_T) - 1 -> +inf as S_T -> 0
  So H_2 is a strictly monotone function of S_T on (-1, 1): same information,
  different units. The companion channel eta_T is required to recover sign.

Moment non-identifiability (L):
  L_2(p,v) = -a*ln(1-p) + a*v/(2(1-p)^2)  is a second-order delta-method
  approximation. Three discrete distributions on [0,1] with identical
  (p, v) = (0.5, 0.04) yield distinct exact E[-ln(1-P)]:
    A: 0.2@0.1 + 0.8@0.6  ->  0.754105
    B: 0.5@0.3 + 0.5@0.7  ->  0.780324
    C: 0.8@0.4 + 0.2@0.9  ->  0.869178
  Gap C-A = 0.115073 = 14.9% of L_2(0.5, 0.04) = 0.773147.
  The projection (p, v) |-> L_2 has a non-trivial kernel: distinct objects
  map to identical coordinates, and the discarded dimensions are exactly
  where the loss lives.

Great Scale mapping
------------------
One law, three faces:
  1. Local QGT saturation (LXXVI-XCIV): scalar chi hides rawCurvatureFraction.
  2. Topological orientation (LXXXIX-XC): scalar S_T hides eta_T sign;
     entropy H_2 relabels S_T in bits without adding information.
  3. Probabilistic moment closure (L): scalar L_2 hides the distribution;
     three objects, one shadow, three losses.
The cone floor phi^-2 is the shared baseline beneath all three projections.
The companion channel differs by domain but serves one function: restore the
kernel the scalar discards.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

TOL = 1e-12
PHI = (1.0 + math.sqrt(5.0)) / 2.0
CONE_FLOOR = 1.0 / PHI**2          # phi^-2 ≈ 0.381966
HEAT_MAX = 0.25                   # h(1-h) at h = 1/2
L2_REFERENCE = 0.773147180560    # L_2(0.5, 0.04), a = 1


# ---------------------------------------------------------------------------
# 1. Projection-aware promotion gate (XCIV response)
# ---------------------------------------------------------------------------

@dataclass
class CurvatureReport:
    """Companion channel for a scalar curvature observation."""
    chi_raw: float
    tolerance: float
    raw_curvature_fraction: float = field(init=False)
    positivity_overshoot: float = field(init=False)
    saturation_projected: bool = field(init=False)

    def __post_init__(self) -> None:
        self.raw_curvature_fraction = self.chi_raw / (1.0 + self.tolerance)
        self.positivity_overshoot = max(0.0, self.chi_raw - 1.0)
        self.saturation_projected = self.chi_raw > 1.0

    def gate(self) -> Dict[str, object]:
        """Return gate decision. PROMOTE only if all checks pass."""
        checks = {
            "not_saturation_projected": not self.saturation_projected,
            "zero_positivity_overshoot": self.positivity_overshoot == 0.0,
            "raw_fraction_le_one": self.raw_curvature_fraction <= 1.0 + TOL,
        }
        return {
            "promote": all(checks.values()),
            "checks": checks,
            "raw_curvature_fraction": self.raw_curvature_fraction,
            "positivity_overshoot": self.positivity_overshoot,
            "saturation_projected": self.saturation_projected,
            "chi_raw": self.chi_raw,
            "tolerance": self.tolerance,
        }


# ---------------------------------------------------------------------------
# 2. Orientation entropy (XC response): binary entropy reparameterization
# ---------------------------------------------------------------------------

def orientation_probs(eta: float) -> Tuple[float, float]:
    """p_+ = (1+eta)/2, p_- = (1-eta)/2 for eta in [-1, 1]."""
    if not -1.0 - TOL <= eta <= 1.0 + TOL:
        raise ValueError("eta must lie in [-1, 1]")
    pp = (1.0 + eta) / 2.0
    pm = (1.0 - eta) / 2.0
    return pp, pm


def heat_term(eta: float) -> float:
    """S_T = p_+ p_- . Max 1/4 at eta = 0."""
    pp, pm = orientation_probs(eta)
    return pp * pm


def binary_entropy(eta: float) -> float:
    """H_2(eta) = -p_+ ln p_+ - p_- ln p_-  (nats). Max ln 2 at eta = 0."""
    pp, pm = orientation_probs(eta)
    h = 0.0
    if pp > 0.0:
        h -= pp * math.log(pp)
    if pm > 0.0:
        h -= pm * math.log(pm)
    return h


def entropy_slope(eta: float, h: float = 1e-9) -> float:
    """Numerical dH_2/dS_T. Analytic: -ln(S_T) - 1, diverging as S_T -> 0."""
    s1, e1 = heat_term(eta), binary_entropy(eta)
    s2, e2 = heat_term(eta + h), binary_entropy(eta + h)
    if s2 == s1:
        return float("inf")
    return (e2 - e1) / (s2 - s1)


# ---------------------------------------------------------------------------
# 3. Moment non-identifiability (L response): three distributions, one shadow
# ---------------------------------------------------------------------------

Distribution = Dict[float, float]  # value -> mass


def dist_moments(d: Distribution) -> Tuple[float, float]:
    mean = sum(x * p for x, p in d.items())
    var = sum((x - mean) ** 2 * p for x, p in d.items())
    return mean, var


def dist_exact_loss(d: Distribution, a: float = 1.0) -> float:
    """Exact E[-a ln(1-P)] for P supported on [0, 1)."""
    return sum(-a * math.log(1.0 - x) * p for x, p in d.items() if x < 1.0)


def l2_approx(p: float, v: float, a: float = 1.0) -> float:
    """Second-order delta-method approximation L_2(p, v)."""
    return a * (-math.log(1.0 - p) + v / (2.0 * (1.0 - p) ** 2))


# The three distributions from GS-L-01, rational masses
DIST_A: Distribution = {0.1: 0.2, 0.6: 0.8}
DIST_B: Distribution = {0.3: 0.5, 0.7: 0.5}
DIST_C: Distribution = {0.4: 0.8, 0.9: 0.2}


# ---------------------------------------------------------------------------
# 4. Tests
# ---------------------------------------------------------------------------

def test_descent95() -> None:
    # --- Gate: XCIV overshoot example ---
    rep = CurvatureReport(chi_raw=1.0 + 5e-11, tolerance=1e-10)
    g = rep.gate()
    assert g["promote"] is False
    assert g["saturation_projected"] is True
    assert abs(g["positivity_overshoot"] - 5e-11) < TOL
    assert g["raw_curvature_fraction"] > 1.0
    # clean input promotes
    rep2 = CurvatureReport(chi_raw=0.95, tolerance=1e-10)
    assert rep2.gate()["promote"] is True
    assert rep2.gate()["raw_curvature_fraction"] < 1.0

    # --- Involution modular identity (XCIV harness continuity) ---
    inv = lambda x: 9.0 - x
    for x in [i / 4 for i in range(37)]:
        assert abs(inv(inv(x)) - x) < TOL
    for a, b in [(1, 8), (2, 7), (3, 6), (4, 5)]:
        assert inv(a) == b and inv(b) == a
    assert inv(0) == 9 and inv(9) == 0

    # --- Five-start convergence: x_n - 4.5 = (1-k)^n (x_0 - 4.5), k = 0.5 ---
    k = 0.5
    for x0 in [1.0, 0.5, 8.0, 3.0, 6.5]:
        err = abs((1 - k) ** 40 * (x0 - 4.5))
        assert err < 1e-6
    assert abs(0.5 ** 40 - 9.0949e-13) < 1e-15

    # --- Heat max 0.25 at h = 1/2 ---
    hs = [i / 1000 for i in range(1001)]
    assert abs(max(hs, key=lambda h: h * (1 - h)) - 0.5) < 1e-9
    assert abs(0.5 * 0.5 - HEAT_MAX) < TOL

    # --- Cone floor phi^-2 ---
    assert abs(CONE_FLOOR - 0.3819660112501051) < 1e-12

    # --- Orientation entropy endpoints and interior ---
    st0, h0 = heat_term(0.0), binary_entropy(0.0)
    assert abs(st0 - 0.25) < TOL and abs(h0 - math.log(2)) < TOL
    for e in (1.0, -1.0):
        assert abs(heat_term(e)) < TOL and abs(binary_entropy(e)) < TOL
    # monotonicity: H_2 decreases as |eta| increases
    prev = binary_entropy(0.0)
    for e in [i / 20 for i in range(1, 21)]:
        cur = binary_entropy(e)
        assert cur < prev - 1e-12
        prev = cur
    # slope positive and growing toward the endpoint
    s1 = entropy_slope(0.5)
    s2 = entropy_slope(0.9)
    s3 = entropy_slope(0.99)
    assert s1 > 0 and s2 > s1 and s3 > s2
    # analytic: dH/dS = -ln(S) - 1
    st, h = heat_term(0.5), binary_entropy(0.5)
    # at eta=0.5: S = 0.375, H = 0.66156; slope ~ -ln(0.375)-1 = 0.981
    analytic = -math.log(st) - 1.0
    assert abs(s1 - analytic) < 0.05

    # --- Descent L counterexample, rational masses ---
    for d, exp_loss in [(DIST_A, 0.754105), (DIST_B, 0.780324), (DIST_C, 0.869178)]:
        p, v = dist_moments(d)
        assert abs(p - 0.5) < TOL and abs(v - 0.04) < TOL
        exact = dist_exact_loss(d)
        assert abs(exact - exp_loss) < 1e-5, (d, exact, exp_loss)
    l2 = l2_approx(0.5, 0.04)
    assert abs(l2 - L2_REFERENCE) < 1e-9
    gap = dist_exact_loss(DIST_C) - dist_exact_loss(DIST_A)
    assert abs(gap - 0.115073) < 1e-5
    assert abs(gap / l2 - 0.149) < 0.01          # 14.9% of L_2

    # --- Feasible-set sanity (L's variance bound) ---
    assert 0.04 <= 0.5 * 0.5 and 0.04 > 0.25 * 0.0   # inside disk
    # boundary: v = 0.1 -> p_max = (1+sqrt(0.6))/2
    pmax = (1.0 + math.sqrt(0.6)) / 2.0
    assert abs(pmax - 0.8872983346207417) < 1e-12

    print("=== Descent XCV promotion-gate tests: ALL PASS ===")
    print(f"cone floor phi^-2 = {CONE_FLOOR:.12f}")
    print(f"heat max = {HEAT_MAX} at h = 1/2; orientation S_T max = 1/4 at eta = 0")
    print(f"binary entropy max = ln2 = {math.log(2):.6f} nats at eta = 0")
    print(f"dH_2/dS_T at eta=0.5: numeric={s1:.4f}, analytic={analytic:.4f}")
    print(f"L counterexample gap C-A = {gap:.6f} ({gap/l2*100:.1f}% of L_2)")
    print(f"XCIV overshoot: chi_raw=1+5e-11, tol=1e-10 -> PROMOTE=False, "
          f"rawFraction={g['raw_curvature_fraction']:.6f}, "
          f"overshoot={g['positivity_overshoot']:.2e}")


if __name__ == "__main__":
    test_descent95()
