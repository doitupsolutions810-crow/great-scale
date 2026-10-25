#!/usr/bin/env python3
"""CXLVII: characterize the quotient seam of the canonical-coordinate contraction.

This is a regression *characterization* of a mathematical defect, not a claim
that the canonical-coordinate formula is continuous on the circle.
"""
import math


def soft_contract(x, k=0.5):
    m = ((x % 9) + 9) % 9
    return 4.5 + k * (m - 4.5)


def circular_distance(a, b):
    d = abs(((a - b) % 9 + 9) % 9)
    return min(d, 9 - d)


def test_fiber_constancy_does_not_imply_continuity():
    # The formula is well-defined on equivalence classes: x ~ x + 9n.
    for x in (-18.25, -4.5, 0.0, 2.0, 4.5, 8.75, 9.0, 13.5, 27.25):
        assert math.isclose(soft_contract(x), soft_contract(x + 9), abs_tol=1e-12)

    # Exact representatives agree at the seam, which alone is insufficient.
    assert math.isclose(soft_contract(0), soft_contract(9), abs_tol=1e-12)

    # But the left-hand limit at 9 is 6.75 while the value at 0 is 2.25.
    eps = 1e-8
    left_limit = soft_contract(9 - eps)
    seam_value = soft_contract(0)
    gap = circular_distance(left_limit, seam_value)
    assert math.isclose(left_limit, 6.75, abs_tol=1e-7)
    assert math.isclose(seam_value, 2.25, abs_tol=1e-12)
    assert math.isclose(gap, 4.5, abs_tol=1e-7)

    # For 0 < |k| < 1, the seam jump is 9|k| in the local lift;
    # it cannot vanish modulo 9 unless k is an integer (thus k=0 here).
    for k in (0.1, 0.25, 0.5, 0.9):
        jump = circular_distance(4.5 + 4.5 * k, 4.5 - 4.5 * k)
        assert jump > 0


if __name__ == "__main__":
    test_fiber_constancy_does_not_imply_continuity()
    print("PASS CXLVII: quotient fiber constancy and exact seam equality coexist with a 4.5-unit one-sided jump")
