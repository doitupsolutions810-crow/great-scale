import unittest
from cxxx_independent_margin_validation import evaluate, run_experiment


class IndependentMarginValidationTests(unittest.TestCase):
    def test_deterministic(self):
        pop = [0.0] * 20 + [0.25] * 5 + [1.0] * 2
        self.assertEqual(evaluate(pop, 0.1, 100, 4), evaluate(pop, 0.1, 100, 4))

    def test_support_margin_contains(self):
        pop = [0.0] * 20 + [0.25] * 5 + [1.0] * 2
        self.assertEqual(evaluate(pop, 1.0, 100, 4)["containment_rate"], 1.0)

    def test_invalid_margin(self):
        with self.assertRaises(ValueError):
            evaluate([0.0, 1.0], -0.1, 10)

    def test_independent_validation_scenarios_present(self):
        result = run_experiment(repetitions=30)
        self.assertEqual(set(result["validation"]), {"rarer_extremes", "more_midrange",
            "shifted_high", "heldout_skewed", "heldout_spiky"})


if __name__ == "__main__":
    unittest.main()
