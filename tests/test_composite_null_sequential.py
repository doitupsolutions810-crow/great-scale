import itertools
import unittest

from composite_null_sequential import bernoulli_upper_null_e_process, sequential_decision


class CompositeSequentialTests(unittest.TestCase):
    def test_starts_at_one_and_returns_each_prefix(self):
        values = bernoulli_upper_null_e_process([1, 0, 1], 0.6, [0.8, 0.9], [0.5, 0.5])
        self.assertEqual(len(values), 4)
        self.assertAlmostEqual(values[0], 1.0)

    def test_finite_horizon_expectation_bound_for_each_null(self):
        q0, n = 0.6, 5
        for q in (0.1, 0.4, 0.6):
            expectation = 0.0
            for xs in itertools.product((0, 1), repeat=n):
                prob = q**sum(xs) * (1-q)**(n-sum(xs))
                e_n = bernoulli_upper_null_e_process(xs, q0, [0.8, 0.95], [0.7, 0.3])[-1]
                expectation += prob * e_n
            self.assertLessEqual(expectation, 1.0 + 1e-10, msg=f"q={q}, expectation={expectation}")

    def test_ville_crossing_probability_enumeration(self):
        alpha, q0, n = 0.05, 0.6, 8
        for q in (0.2, 0.6):
            crossing_probability = 0.0
            for xs in itertools.product((0, 1), repeat=n):
                prob = q**sum(xs) * (1-q)**(n-sum(xs))
                values = bernoulli_upper_null_e_process(xs, q0, [0.8], [1.0])
                if max(values) >= 1 / alpha:
                    crossing_probability += prob
            self.assertLessEqual(crossing_probability, alpha + 1e-12)

    def test_assumption_gate(self):
        self.assertEqual(sequential_decision([1, 100], 0.05, assumptions_confirmed=False), "ASSUMPTIONS_NOT_CONFIRMED")

    def test_threshold_crossing(self):
        self.assertEqual(sequential_decision([1, 20], 0.05), "REJECT_NULL_SEQUENTIALLY")
        self.assertEqual(sequential_decision([1, 2], 0.05), "NO_THRESHOLD_CROSSING")

    def test_rejects_alternative_not_above_null_bound(self):
        with self.assertRaises(ValueError):
            bernoulli_upper_null_e_process([1], 0.6, [0.6], [1.0])

    def test_rejects_bad_weights(self):
        with self.assertRaises(ValueError):
            bernoulli_upper_null_e_process([1], 0.6, [0.8, 0.9], [0.5, 0.2])

    def test_rejects_invalid_observations(self):
        with self.assertRaises(ValueError):
            bernoulli_upper_null_e_process([1, 2], 0.6, [0.8], [1.0])


if __name__ == "__main__":
    unittest.main()
