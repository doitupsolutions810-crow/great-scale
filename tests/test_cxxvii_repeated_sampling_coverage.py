import unittest
from cxxvii_repeated_sampling_coverage import finite_population_bounds, run_coverage_experiment


class CoverageDiagnosticTests(unittest.TestCase):
    def test_finite_population_formula(self):
        self.assertEqual(finite_population_bounds([0.0, 0.5], 4, 0.0, 1.0), (0.125, 0.625))

    def test_rejects_invalid_support(self):
        with self.assertRaises(ValueError):
            finite_population_bounds([2.0], 2, 0.0, 1.0)

    def test_reproducible_and_domain_support_covers(self):
        a = run_coverage_experiment(repetitions=300, seed=17)
        b = run_coverage_experiment(repetitions=300, seed=17)
        self.assertEqual(a, b)
        self.assertEqual(a["coverage_rate"]["known_support"], 1.0)

    def test_empirical_extrema_are_not_guaranteed(self):
        result = run_coverage_experiment(repetitions=1000, seed=20261010)
        self.assertLess(result["coverage_rate"]["sample_extrema"], 1.0)


if __name__ == "__main__":
    unittest.main()
