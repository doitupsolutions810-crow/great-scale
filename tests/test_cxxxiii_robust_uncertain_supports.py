import unittest
from cxxxiii_robust_uncertain_supports import (
    UncertainStratum, robust_bounds, global_bounds, width_condition, demo
)


class RobustUncertainSupportTests(unittest.TestCase):
    def setUp(self):
        self.strata = [
            UncertainStratum(100, (0.0,) * 20 + (0.1,) * 20, 0.0, 0.05, 0.15, 0.2),
            UncertainStratum(100, (0.4,) * 20 + (0.6,) * 20, 0.35, 0.4, 0.9, 1.0),
        ]

    def test_robust_bounds(self):
        b = robust_bounds(self.strata)
        self.assertAlmostEqual(b.lower, 0.215)
        self.assertAlmostEqual(b.upper, 0.47)
        self.assertAlmostEqual(b.width, 0.255)

    def test_global_comparison(self):
        b = global_bounds(self.strata, 0.0, 1.0)
        self.assertAlmostEqual(b.lower, 0.11)
        self.assertAlmostEqual(b.upper, 0.71)
        self.assertAlmostEqual(b.width, 0.60)

    def test_weighted_span_condition_predicts_tightening(self):
        c = width_condition(self.strata, 0.0, 1.0)
        self.assertTrue(c["strictly_tighter"])
        self.assertAlmostEqual(c["robust_width"], 0.255)
        self.assertAlmostEqual(c["global_width"], 0.60)

    def test_no_tightening_when_local_spans_match_global(self):
        strata = [UncertainStratum(2, (0.25,), 0.0, 0.0, 1.0, 1.0)]
        c = width_condition(strata, 0.0, 1.0)
        self.assertTrue(c["equal_width"])
        self.assertFalse(c["strictly_tighter"])

    def test_rejects_inconsistent_endpoint_ranges(self):
        bad = [UncertainStratum(2, (0.2,), 0.5, 0.4, 0.8, 1.0)]
        with self.assertRaises(ValueError):
            robust_bounds(bad)

    def test_rejects_observation_outside_outer_support(self):
        bad = [UncertainStratum(2, (0.9,), 0.0, 0.1, 0.4, 0.5)]
        with self.assertRaises(ValueError):
            robust_bounds(bad)

    def test_demo_discloses_assumption(self):
        self.assertIn("assumed", demo()["status"])


if __name__ == "__main__":
    unittest.main()
