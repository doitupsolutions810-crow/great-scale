import itertools
import math
import unittest
from predictable_adaptive_eprocess import predictable_adaptive_e_process

class PredictableAdaptiveTests(unittest.TestCase):
    def test_history_adaptive_strategy_receives_only_past(self):
        seen = []
        def strategy(history):
            seen.append(history)
            return 0.5 if sum(history) % 2 == 0 else 1.0
        values = predictable_adaptive_e_process([1, 0, 1], 0.5, [strategy], [1.0])
        self.assertEqual(seen, [(), (1,), (1, 0)])
        self.assertEqual(len(values), 4)

    def test_constant_strategy_matches_cii(self):
        values = predictable_adaptive_e_process([1, 1, 0], 0.5, [lambda h: 1.0], [1.0])
        self.assertEqual(values, [1.0, 1.5, 2.25, 1.125])

    def test_exhaustive_expected_e_at_most_one(self):
        q0 = 0.5
        def adaptive(history): return 0.5 if len(history) % 2 == 0 else 1.0
        for q in (0.1, 0.3, 0.5):
            for n in range(1, 8):
                mean = 0.0
                for seq in itertools.product((0, 1), repeat=n):
                    probability = math.prod(q if x else 1-q for x in seq)
                    mean += probability * predictable_adaptive_e_process(seq, q0, [adaptive], [1.0])[-1]
                self.assertLessEqual(mean, 1.0 + 1e-10)

    def test_invalid_bet_rejected(self):
        with self.assertRaises(ValueError): predictable_adaptive_e_process([1], 0.5, [lambda h: 2.1], [1.0])
    def test_invalid_weights_rejected(self):
        with self.assertRaises(ValueError): predictable_adaptive_e_process([1], 0.5, [lambda h: 0.5], [0.8])
    def test_invalid_observation_rejected(self):
        with self.assertRaises(ValueError): predictable_adaptive_e_process([2], 0.5, [lambda h: 0.5], [1.0])

if __name__ == "__main__": unittest.main()
