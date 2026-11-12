import unittest
from cxxv_robust_stratum_bound_uncertainty import (
    robust_stratified_bounds, nominal_stratified_bounds,
)


class RobustStratumBoundTests(unittest.TestCase):
    def test_uncertain_limits_widen_bounds(self):
        nominal = {"A": {"total_count": 4, "observed_values": [0.0], "lower": 0.0, "upper": 0.25}}
        uncertain = {"A": {"total_count": 4, "observed_values": [0.0],
                            "lower_range": (0.0, 0.02), "upper_range": (0.25, 0.30)}}
        n = nominal_stratified_bounds(nominal)
        r = robust_stratified_bounds(uncertain)
        self.assertLessEqual(r["lower_bound"], n["lower_bound"])
        self.assertGreaterEqual(r["upper_bound"], n["upper_bound"])
        self.assertGreater(r["width"], n["width"])

    def test_point_ranges_match_nominal(self):
        data = {"A": {"total_count": 3, "observed_values": [0.0],
                      "lower_range": (0.0, 0.0), "upper_range": (0.5, 0.5)}}
        result = robust_stratified_bounds(data)
        self.assertAlmostEqual(result["lower_bound"], 0.0)
        self.assertAlmostEqual(result["upper_bound"], 1.0 / 3)

    def test_rejects_inconsistent_limit_ranges(self):
        data = {"A": {"total_count": 2, "observed_values": [],
                      "lower_range": (0.2, 0.1), "upper_range": (0.3, 0.4)}}
        with self.assertRaises(ValueError):
            robust_stratified_bounds(data)

    def test_rejects_observation_outside_outer_limits(self):
        data = {"A": {"total_count": 1, "observed_values": [0.6],
                      "lower_range": (0.0, 0.0), "upper_range": (0.3, 0.4)}}
        with self.assertRaises(ValueError):
            robust_stratified_bounds(data)


if __name__ == "__main__":
    unittest.main()
