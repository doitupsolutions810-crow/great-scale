import unittest

from observability_limits import (
    detection_power_upper_bound,
    detector_disposition,
    distinguishability_gap,
    minimum_tv_needed,
)


class ObservabilityLimitsTests(unittest.TestCase):
    def test_identical_observations_cannot_exceed_false_positive_rate(self):
        self.assertAlmostEqual(detection_power_upper_bound(0.05, 0.0), 0.05)

    def test_power_upper_bound(self):
        self.assertAlmostEqual(detection_power_upper_bound(0.05, 0.20), 0.25)

    def test_power_bound_caps_at_one(self):
        self.assertEqual(detection_power_upper_bound(0.8, 0.7), 1.0)

    def test_minimum_separation_needed(self):
        self.assertAlmostEqual(minimum_tv_needed(0.05, 0.90), 0.85)

    def test_disposition_does_not_overclaim(self):
        self.assertEqual(detector_disposition(0.05, 0.10, 0.90), "POWER_REQUIREMENT_IMPOSSIBLE_UNDER_BOUND")
        self.assertEqual(detector_disposition(0.05, 0.90, 0.90), "POWER_POSSIBLE_NOT_GUARANTEED")

    def test_distinguishability_gap(self):
        self.assertEqual(distinguishability_gap(0.0), 0.0)

    def test_invalid_inputs(self):
        for bad in (-0.1, 1.1):
            with self.assertRaises(ValueError):
                distinguishability_gap(bad)
