import unittest

from cxxxii_justified_strata_tightening import (
    Stratum, stratified_bounds, global_support_bounds, endpoints_are_attainable, demo
)


class JustifiedStrataTests(unittest.TestCase):
    def setUp(self):
        self.strata = [
            Stratum(100, (0.0,) * 20 + (0.1,) * 20, 0.0, 0.2),
            Stratum(100, (0.4,) * 20 + (0.6,) * 20, 0.4, 1.0),
        ]

    def test_bounds_and_width(self):
        b = stratified_bounds(self.strata)
        self.assertAlmostEqual(b.lower, 0.23)
        self.assertAlmostEqual(b.upper, 0.47)
        self.assertAlmostEqual(b.width, 0.24)

    def test_tighter_than_global_support(self):
        narrow = stratified_bounds(self.strata)
        broad = global_support_bounds(self.strata, 0.0, 1.0)
        self.assertAlmostEqual(broad.lower, 0.11)
        self.assertAlmostEqual(broad.upper, 0.71)
        self.assertLess(narrow.width, broad.width)

    def test_endpoints_are_attainable(self):
        self.assertTrue(endpoints_are_attainable(self.strata))

    def test_rejects_observed_value_outside_declared_support(self):
        bad = [Stratum(2, (0.8,), 0.0, 0.5)]
        with self.assertRaises(ValueError):
            stratified_bounds(bad)

    def test_rejects_more_observations_than_population(self):
        bad = [Stratum(1, (0.0, 0.1), 0.0, 1.0)]
        with self.assertRaises(ValueError):
            stratified_bounds(bad)

    def test_demo_reports_assumption(self):
        result = demo()
        self.assertTrue(result["endpoint_attainability_checked"])
        self.assertIn("assumption", result["status"])


if __name__ == "__main__":
    unittest.main()
