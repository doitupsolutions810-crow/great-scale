import unittest
from cxxxi_sharp_support_bound_test import support_bounds, auxiliary_margin_bounds, evaluate


class SharpSupportBoundTests(unittest.TestCase):
    def test_sharp_support_formula(self):
        self.assertEqual(support_bounds([0.0, 0.5], 4), (0.125, 0.625))

    def test_auxiliary_interval_is_inside_support_interval(self):
        obs = [0.0, 0.5]
        sharp = support_bounds(obs, 4)
        aux = auxiliary_margin_bounds(obs, [0.25, 0.5], 4, 0.1)
        self.assertGreaterEqual(aux[0], sharp[0])
        self.assertLessEqual(aux[1], sharp[1])

    def test_support_bound_always_contains_population_mean(self):
        pop = [0.0] * 20 + [0.25] * 5 + [1.0] * 2
        result = evaluate(pop, repetitions=100, seed=3)
        self.assertEqual(result["support_bound_empirical_containment"], 1.0)

    def test_invalid_support_sample(self):
        with self.assertRaises(ValueError):
            support_bounds([2.0], 2)


if __name__ == "__main__":
    unittest.main()
