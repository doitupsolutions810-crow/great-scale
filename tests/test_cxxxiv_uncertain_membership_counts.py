import unittest
from cxxxiv_uncertain_membership_counts import StratumCountRange, robust_count_bounds, demo


class UncertainMembershipTests(unittest.TestCase):
    def setUp(self):
        self.strata = [
            StratumCountRange(2.0, 40, 40, 80, 0.0, 0.2),
            StratumCountRange(20.0, 40, 40, 80, 0.4, 1.0),
        ]

    def test_worst_case_bounds_and_allocations(self):
        b = robust_count_bounds(self.strata, 120)
        self.assertAlmostEqual(b.lower, 0.23)
        self.assertAlmostEqual(b.upper, 0.47)
        self.assertEqual(b.lower_allocation, (80, 40))
        self.assertEqual(b.upper_allocation, (40, 80))

    def test_rejects_infeasible_total(self):
        with self.assertRaises(ValueError):
            robust_count_bounds(self.strata, 50)

    def test_rejects_invalid_support(self):
        bad = [StratumCountRange(0, 1, 0, 1, 1.0, 0.0)]
        with self.assertRaises(ValueError):
            robust_count_bounds(bad, 1)

    def test_demo_discloses_assumptions(self):
        self.assertIn("assumptions", demo()["status"])


if __name__ == "__main__":
    unittest.main()
