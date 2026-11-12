import itertools
import math
import unittest

from composite_null_evidence import fixed_sample_decision, fixed_sample_robust_e_value


class CompositeNullEvidenceTests(unittest.TestCase):
    def test_finite_null_expectation_bound_by_enumeration(self):
        nulls = [0.25, 0.5, 0.75]
        alts = [0.2, 0.8]
        weights = [0.5, 0.5]
        n = 4
        for q in nulls:
            expectation = 0.0
            for xs in itertools.product((0, 1), repeat=n):
                s = sum(xs)
                probability = q**s * (1-q)**(n-s)
                e = fixed_sample_robust_e_value(xs, nulls, alts, weights)
                expectation += probability * e
            self.assertLessEqual(expectation, 1.0 + 1e-12, msg=f"q={q}: {expectation}")

    def test_example_is_finite_and_positive(self):
        e = fixed_sample_robust_e_value([1, 1, 1], [0.4, 0.5, 0.6], [0.8, 0.2], [0.5, 0.5])
        self.assertTrue(math.isfinite(e))
        self.assertGreater(e, 0)

    def test_threshold_decision(self):
        self.assertEqual(fixed_sample_decision(20.0, 0.05), "REJECT_NULL_AT_FIXED_SAMPLE")
        self.assertEqual(fixed_sample_decision(19.999, 0.05), "INSUFFICIENT_EVIDENCE")

    def test_assumption_gate(self):
        self.assertEqual(fixed_sample_decision(100.0, 0.05, assumptions_confirmed=False), "ASSUMPTIONS_NOT_CONFIRMED")

    def test_empty_observations_rejected(self):
        with self.assertRaises(ValueError):
            fixed_sample_robust_e_value([], [0.5], [0.8], [1.0])

    def test_invalid_observation_rejected(self):
        with self.assertRaises(ValueError):
            fixed_sample_robust_e_value([0, 2], [0.5], [0.8], [1.0])

    def test_weight_sum_required(self):
        with self.assertRaises(ValueError):
            fixed_sample_robust_e_value([1], [0.5], [0.8, 0.7], [0.5, 0.4])

    def test_all_nulls_assign_zero_probability_rejected(self):
        with self.assertRaises(ValueError):
            fixed_sample_robust_e_value([1, 0], [0.0, 1.0], [0.8], [1.0])

    def test_zero_weight_component_is_ignored(self):
        e = fixed_sample_robust_e_value([1, 1], [0.5], [0.8, 0.2], [1.0, 0.0])
        self.assertAlmostEqual(e, (0.8**2)/(0.5**2))


if __name__ == "__main__":
    unittest.main()
