import unittest
from residual_risk import surviving_paths, state_probability, modeled_reliability, interval_reliability_bounds, incompleteness_adjusted_bounds

class ResidualRiskTests(unittest.TestCase):
    def test_shared_failure(self):
        paths = {"A": {"calibration", "sensor_a"}, "B": {"calibration", "lab_b"}, "C": {"reference", "sensor_c"}}
        self.assertEqual(surviving_paths(paths, {"calibration"}), ["C"])

    def test_state_probability(self):
        self.assertAlmostEqual(state_probability({"a": 0.2, "b": 0.5}, {"a"}), 0.1)

    def test_exact_reliability(self):
        self.assertAlmostEqual(modeled_reliability({"A": {"a"}, "B": {"b"}}, {"a": 0.1, "b": 0.2}, 2), 0.72)

    def test_interval_bounds(self):
        lo, hi = interval_reliability_bounds({"A": {"a"}}, {"a": (0.1, 0.3)}, 1)
        self.assertAlmostEqual(lo, 0.7)
        self.assertAlmostEqual(hi, 0.9)

    def test_incompleteness_bounds(self):
        self.assertEqual(incompleteness_adjusted_bounds(0.9, 0.1), (0.81, 0.91))

    def test_invalid_probability(self):
        with self.assertRaises(ValueError):
            modeled_reliability({"A": {"a"}}, {"a": 1.2}, 1)

if __name__ == "__main__":
    unittest.main()
