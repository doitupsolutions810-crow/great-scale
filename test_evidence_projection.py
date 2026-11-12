#!/usr/bin/env python3
"""Regression checks for Descent XCVII: a geometry scalar is not an auth proof."""
import math

TOL = 1e-10
PHI = (1 + math.sqrt(5)) / 2
CONE = (PHI - 1) ** 2


def heat(h):
    return h * (1 - h)


def project_qgt(g11, g12, g22, curvature):
    det_g = g11 * g22 - g12 * g12
    if g11 <= 0 or g22 <= 0 or det_g <= 0:
        raise ValueError("metric must be positive definite")
    chi_raw = abs(curvature) / (2 * math.sqrt(det_g))
    if chi_raw > 1 + TOL:
        raise ValueError("QGT positivity violated")
    chi = min(1.0, chi_raw)
    s_q = heat((1 + chi) / 2)
    return chi, s_q, CONE + s_q


def test_orientation_is_lost_by_scalar_projection():
    plus = project_qgt(2.0, 0.25, 3.0, 0.5)
    minus = project_qgt(2.0, 0.25, 3.0, -0.5)
    assert plus[0] == minus[0]
    assert plus[1] == minus[1]
    assert plus[2] == minus[2]


def test_common_positive_scale_is_invariant():
    baseline = project_qgt(2.0, 0.25, 3.0, 0.5)
    for scale in (1e-100, 1.0, 1e100):
        scaled = project_qgt(
            2.0 * scale, 0.25 * scale, 3.0 * scale, 0.5 * scale
        )
        assert math.isclose(scaled[0], baseline[0], rel_tol=1e-12, abs_tol=1e-14)
        assert math.isclose(scaled[1], baseline[1], rel_tol=1e-12, abs_tol=1e-14)
        assert math.isclose(scaled[2], baseline[2], rel_tol=1e-12, abs_tol=1e-14)


def test_cone_floor_is_preserved():
    for curvature in (0.0, 0.5, 1.0, 2.0):
        _, s_q, psi_q = project_qgt(2.0, 0.0, 3.0, curvature)
        assert -1e-14 <= s_q <= 0.25 + 1e-14
        assert psi_q >= CONE


def test_equal_scalar_does_not_imply_equal_authority():
    # Same displayed geometry scalar; different rights must still yield
    # different authorization outcomes. The scalar is not a credential.
    scalar = 0.2
    read_only = {
        "scale_scalar": scalar,
        "audience": "agent-A",
        "rights": {"read:state"},
    }
    execute_cap = {
        "scale_scalar": scalar,
        "audience": "agent-A",
        "rights": {"execute:tool"},
    }
    assert read_only["scale_scalar"] == execute_cap["scale_scalar"]
    assert ("execute:tool" in read_only["rights"]) is False
    assert ("execute:tool" in execute_cap["rights"]) is True
    # A decision based only on the scalar cannot distinguish these claims.


def test_invalid_qgt_bound_is_rejected():
    try:
        project_qgt(1.0, 0.0, 1.0, 2.0 * (1 + 2 * TOL))
    except ValueError:
        return
    raise AssertionError("QGT positivity violation was accepted")


if __name__ == "__main__":
    tests = [
        test_orientation_is_lost_by_scalar_projection,
        test_common_positive_scale_is_invariant,
        test_cone_floor_is_preserved,
        test_equal_scalar_does_not_imply_equal_authority,
        test_invalid_qgt_bound_is_rejected,
    ]
    for test_case in tests:
        test_case()
        print("PASS", test_case.__name__)
    print(f"{len(tests)} evidence-projection checks passed")
