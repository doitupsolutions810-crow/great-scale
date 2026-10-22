import unittest
from cxxiv_stratified_population_bounds import (
    stratified_population_bounds, unstratified_bounds,
)


class StratifiedBoundsTests(unittest.TestCase):
    def test_known_example_and_tightening(self):
        data = {
            "A": {"total_count": 4, "observed_values": [0.0], "lower": 0.0, "upper": 0.25},
            "B": {"total_count": 4, "observed_values": [0.125], "lower": 0.0, "upper": 0.125},
        }
        result = stratified_population_bounds(data)
        global_result = unstratified_bounds(data, 0.0, 0.25)
        self.assertAlmostEqual(result["lower_bound"], 0.015625)
        self.assertAlmostEqual(result["upper_bound"], 0.15625)
        self.assertLessEqual(result["width"], global_result["width"])

    def test_complete_population_collapses_to_point(self):
        data = {"x": {"total_count": 2, "observed_values": [0.0, 0.5], "lower": 0.0, "upper": 0.5}}
        result = stratified_population_bounds(data)
        self.assertEqual(result["lower_bound"], result["upper_bound"])
        self.assertEqual(result["width"], 0.0)

    def test_rejects_out_of_bounds_observation(self):
        data = {"x": {"total_count": 1, "observed_values": [0.6], "lower": 0.0, "upper": 0.5}}
        with self.assertRaises(ValueError):
            stratified_population_bounds(data)

    def test_rejects_observed_count_above_total(self):
        data = {"x": {"total_count": 1, "observed_values": [0.0, 0.0], "lower": 0.0, "upper": 0.5}}
        with self.assertRaises(ValueError):
            stratified_population_bounds(data)


if __name__ == "__main__":
    unittest.main()
