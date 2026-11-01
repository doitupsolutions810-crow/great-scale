import unittest
from cxxviii_margin_coverage_frontier import finite_population_bounds, run_margin_sweep


class MarginCoverageFrontierTests(unittest.TestCase):
    def test_bound_formula(self):
        self.assertEqual(finite_population_bounds([0.0, 0.5], 4, 0.0, 1.0), (0.125, 0.625))

    def test_invalid_margin_rejected(self):
        with self.assertRaises(ValueError):
            run_margin_sweep(repetitions=10, margins=(-0.1,))

    def test_monotone_width_and_reproducibility(self):
        a = run_margin_sweep(repetitions=200, seed=22, margins=(0, 0.1, 0.5))
        b = run_margin_sweep(repetitions=200, seed=22, margins=(0, 0.1, 0.5))
        self.assertEqual(a, b)
        widths = [row["mean_interval_width"] for row in a["results"]]
        self.assertEqual(widths, sorted(widths))

    def test_known_support_margin_covers_by_construction(self):
        result = run_margin_sweep(repetitions=100, margins=(1.0,))
        self.assertEqual(result["results"][0]["empirical_containment_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
