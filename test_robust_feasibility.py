"""Regression tests for exact bounded-uncertainty feasibility certificates."""
import unittest
from fractions import Fraction

from robust_feasibility import certify_probability_moment


class RobustFeasibilityTests(unittest.TestCase):
    def test_certifies_entire_box_feasible(self):
        result = certify_probability_moment(0.8, 0.15, 0.01, 0.002)
        self.assertEqual(result.status, "certified_feasible")
        self.assertGreaterEqual(result.lower_margin, 0)
        self.assertEqual(result.lower_margin, Fraction(19, 10000))

    def test_preserves_unresolved_boundary_case(self):
        result = certify_probability_moment(0.5, 0.249, 0.02, 0.001)
        self.assertEqual(result.status, "unresolved")
        self.assertLess(result.lower_margin, 0)
        self.assertGreaterEqual(result.upper_margin, 0)

    def test_certifies_infeasible_when_no_box_point_can_satisfy_constraint(self):
        result = certify_probability_moment(0.5, 0.3, 0.01, 0.01)
        self.assertEqual(result.status, "certified_infeasible")
        self.assertLess(result.upper_margin, 0)

    def test_exact_boundary_is_feasible(self):
        result = certify_probability_moment("0.5", "0.25")
        self.assertEqual(result.status, "certified_feasible")
        self.assertEqual(result.lower_margin, Fraction(0))
        self.assertEqual(result.upper_margin, Fraction(0))

    def test_unresolved_when_upper_margin_is_exactly_zero(self):
        # p in [0.10, 0.20] has max p(1-p)=0.16; v=0.16 touches feasibility
        # at one endpoint but does not make every point in the box feasible.
        result = certify_probability_moment("0.15", "0.16", "0.05", 0)
        self.assertEqual(result.status, "unresolved")
        self.assertLess(result.lower_margin, 0)
        self.assertEqual(result.upper_margin, Fraction(0))

    def test_maximum_occurs_at_endpoint_when_interval_avoids_half(self):
        # For p in [0.80, 0.90], p(1-p) decreases, so the maximum is 0.16.
        result = certify_probability_moment("0.85", "0.08", "0.05", 0)
        self.assertEqual(result.status, "certified_feasible")
        self.assertEqual(result.upper_margin, Fraction(8, 100))

    def test_rejects_invalid_inputs(self):
        for args in [
            (1.1, 0.1, 0, 0),
            (0.5, -0.1, 0, 0),
            (0.5, 0.1, -0.01, 0),
            (0.5, 0.1, 0, -0.01),
            (float("nan"), 0.1, 0, 0),
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                certify_probability_moment(*args)

    def test_uncertainty_box_is_clipped_to_declared_domain(self):
        result = certify_probability_moment(0.02, 0.001, 0.05, 0.001)
        self.assertEqual(result.p_interval[0], Fraction(0))
        self.assertEqual(result.p_interval[1], Fraction(7, 100))
        self.assertEqual(result.v_interval[0], Fraction(0))

    def test_large_exact_uncertainty_does_not_overflow_through_float(self):
        # An exact finite rational can exceed IEEE-754 range. It is still a
        # valid uncertainty bound and should be clipped by the model domain.
        huge = Fraction(10**400)
        result = certify_probability_moment("0.5", "0.1", huge, 0)
        self.assertEqual(result.p_interval, (Fraction(0), Fraction(1)))
        self.assertEqual(result.status, "unresolved")

    def test_rejects_infinite_float(self):
        with self.assertRaises(ValueError):
            certify_probability_moment(0.5, 0.1, float("inf"), 0)


if __name__ == "__main__":
    unittest.main()
