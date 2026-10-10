import unittest
from great_scale.math import weighted_time_variance, pairwise_weighted_time_variance, relaxation_step

class GreatScaleMathTests(unittest.TestCase):
    def test_single_duration_has_zero_frequency_information_factor(self):
        self.assertEqual(weighted_time_variance([3.0, 3.0, 3.0], [1, 2, 4]), 0.0)

    def test_pairwise_identity_matches_centered_variance(self):
        times, weights = [0.0, 1.5, 4.0], [2.0, 1.0, 3.0]
        self.assertAlmostEqual(weighted_time_variance(times, weights), pairwise_weighted_time_variance(times, weights), places=12)

    def test_mean_is_preserved_by_relaxation(self):
        values = [0.0, 2.0, 7.0, 9.0]
        result = relaxation_step(values, 0.35)
        self.assertAlmostEqual(sum(values) / len(values), sum(result) / len(result), places=12)

    def test_relaxation_reduces_deviation(self):
        values = [0.0, 2.0, 7.0, 9.0]
        result = relaxation_step(values, 0.35)
        mean = sum(values) / len(values)
        self.assertLess(sum((x-mean)**2 for x in result), sum((x-mean)**2 for x in values))

if __name__ == '__main__':
    unittest.main()
