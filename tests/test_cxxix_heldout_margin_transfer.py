import unittest
from cxxix_heldout_margin_transfer import evaluate, run_transfer_experiment


class HeldoutTransferTests(unittest.TestCase):
    def test_reproducible(self):
        population = [0.0] * 20 + [0.25] * 5 + [1.0] * 2
        self.assertEqual(evaluate(population, repetitions=100, seed=7),
                         evaluate(population, repetitions=100, seed=7))

    def test_known_support_baseline(self):
        result = evaluate([0.0] * 20 + [0.25] * 5 + [1.0] * 2,
                          margins=(1.0,), repetitions=100, seed=9)
        self.assertEqual(result["results"][0]["empirical_containment_rate"], 1.0)

    def test_rejects_negative_margin(self):
        with self.assertRaises(ValueError):
            evaluate([0.0, 1.0], margins=(-0.1,), repetitions=5)

    def test_scenario_grid(self):
        result = run_transfer_experiment(repetitions=20)
        self.assertEqual(set(result["scenarios"]),
                         {"original", "rarer_extremes", "more_midrange", "shifted_high"})


if __name__ == "__main__":
    unittest.main()
