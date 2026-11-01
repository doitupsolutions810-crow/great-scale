import unittest
from cxxvi_calibrated_auxiliary_bounds import calibrate_outer_limits, population_mean_bounds, build_bounds_from_auxiliary


class AuxiliaryBoundsTests(unittest.TestCase):
    def test_margin_expands_observed_range(self):
        self.assertEqual(calibrate_outer_limits([0.1, 0.3], 0.05), (0.05, 0.35))

    def test_margin_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            calibrate_outer_limits([0.0, 1.0], -0.1)

    def test_missing_extreme_can_break_unexpanded_calibration(self):
        aux = {"A": [0.0, 0.0, 0.0]}
        observed = {"A": [0.0]}
        nominal = build_bounds_from_auxiliary(aux, observed, {"A": 4}, 0.0)
        # True finite population [0, 0, 0, 1] has mean .25, but aux-derived
        # max is zero; this demonstrates that empirical extrema aren't guarantees.
        self.assertEqual(nominal["upper_bound"], 0.0)
        self.assertGreater(0.25, nominal["upper_bound"])

    def test_population_bounds(self):
        r = population_mean_bounds({"A": {"total_count": 4, "observed_values": [0.0],
                                          "lower": 0.0, "upper": 1.0}})
        self.assertEqual(r["lower_bound"], 0.0)
        self.assertEqual(r["upper_bound"], 0.75)


if __name__ == "__main__":
    unittest.main()
