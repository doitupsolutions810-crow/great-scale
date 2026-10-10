import itertools
import math
import unittest

from conditional_mean_eprocess import conditional_mean_e_process, sequential_decision


class ConditionalMeanEProcessTests(unittest.TestCase):
    def test_starts_at_one_and_returns_prefixes(self):
        values = conditional_mean_e_process([1, 0, 1], 0.5, [0.5, 1.0], [0.5, 0.5])
        self.assertEqual(len(values), 4)
        self.assertAlmostEqual(values[0], 1.0)

    def test_factors_nonnegative_at_boundary_bet(self):
        values = conditional_mean_e_process([0, 1], 0.5, [2.0], [1.0])
        self.assertEqual(values[1], 0.0)
        self.assertAlmostEqual(values[2], 1.0)

    def test_expected_final_e_value_at_most_one_for_iid_nulls(self):
        for q in (0.1, 0.4, 0.6):
            for n in range(1, 9):
                mean = 0.0
                for seq in itertools.product((0, 1), repeat=n):
                    prob = math.prod(q if x else 1 - q for x in seq)
                    ev = conditional_mean_e_process(seq, 0.6, [0.25, 0.75, 1.0], [0.2, 0.3, 0.5])[-1]
                    mean += prob * ev
                self.assertLessEqual(mean, 1.0 + 1e-10)

    def test_decision_threshold(self):
        self.assertEqual(sequential_decision([1, 20], 0.05)["status"], "EVIDENCE_THRESHOLD_CROSSED")
        self.assertEqual(sequential_decision([1, 19.9], 0.05)["status"], "NO_THRESHOLD_CROSSING")

    def test_assumption_gate(self):
        out = sequential_decision([100], 0.05, assumptions_confirmed=False)
        self.assertEqual(out["status"], "UNVERIFIED_ASSUMPTIONS")
        self.assertTrue(out["threshold_crossed"])

    def test_invalid_q0(self):
        with self.assertRaises(ValueError):
            conditional_mean_e_process([1], 0, [0.5], [1])

    def test_invalid_bet(self):
        with self.assertRaises(ValueError):
            conditional_mean_e_process([1], 0.5, [2.1], [1])

    def test_invalid_weights(self):
        with self.assertRaises(ValueError):
            conditional_mean_e_process([1], 0.5, [0.5], [0.8])

    def test_invalid_observation(self):
        with self.assertRaises(ValueError):
            conditional_mean_e_process([0, 2], 0.5, [0.5], [1])


if __name__ == "__main__":
    unittest.main()
