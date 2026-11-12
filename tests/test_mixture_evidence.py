import math
import unittest
from mixture_evidence import bernoulli_mixture_e_value, threshold_reached


class MixtureEvidenceTests(unittest.TestCase):
    def test_single_alternative_matches_simple_lr(self):
        e = bernoulli_mixture_e_value([1, 1], 0.5, [0.8], [1.0])
        self.assertAlmostEqual(e, 2.56)

    def test_equal_weight_mixture(self):
        e = bernoulli_mixture_e_value([1, 1], 0.5, [0.8, 0.6], [0.5, 0.5])
        self.assertAlmostEqual(e, 0.5 * 2.56 + 0.5 * 1.44)

    def test_threshold(self):
        self.assertTrue(threshold_reached(20, 0.05))
        self.assertFalse(threshold_reached(19.9, 0.05))

    def test_weights_must_sum_to_one(self):
        with self.assertRaises(ValueError):
            bernoulli_mixture_e_value([1], 0.5, [0.7, 0.8], [0.2, 0.2])

    def test_lengths_must_match(self):
        with self.assertRaises(ValueError):
            bernoulli_mixture_e_value([1], 0.5, [0.7, 0.8], [1.0])

    def test_null_must_be_non_degenerate(self):
        with self.assertRaises(ValueError):
            bernoulli_mixture_e_value([1], 0.0, [0.8], [1.0])

    def test_invalid_observations(self):
        with self.assertRaises(ValueError):
            bernoulli_mixture_e_value([1, 2], 0.5, [0.8], [1.0])

    def test_invalid_alpha(self):
        with self.assertRaises(ValueError):
            threshold_reached(20, 0)

    def test_all_zero_weight_rejected_by_sum(self):
        with self.assertRaises(ValueError):
            bernoulli_mixture_e_value([1], 0.5, [0.8, 0.7], [0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
