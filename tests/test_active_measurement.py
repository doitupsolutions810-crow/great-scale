import math
import unittest
from active_measurement import entropy, information_gain, expected_value_of_sample_information

class ActiveMeasurementTests(unittest.TestCase):
    def test_entropy_binary_fair_prior(self):
        self.assertAlmostEqual(entropy([0.5, 0.5]), math.log(2))
    def test_perfect_measurement_reveals_full_binary_entropy(self):
        self.assertAlmostEqual(information_gain([0.5, 0.5], [[1, 0], [0, 1]]), math.log(2))
    def test_uninformative_measurement_has_zero_gain(self):
        self.assertAlmostEqual(information_gain([0.5, 0.5], [[0.3, 0.7], [0.3, 0.7]]), 0.0)
    def test_measurement_value_can_change_decision(self):
        r = expected_value_of_sample_information([0.5, 0.5], [[1, 0], [0, 1]], [[1, -1], [-1, 1]], 0.2)
        self.assertAlmostEqual(r["evsi"], 1.0); self.assertAlmostEqual(r["net_value"], 0.8)
        self.assertEqual(r["recommendation"], "MEASURE")
    def test_cost_can_exceed_decision_value(self):
        r = expected_value_of_sample_information([0.5, 0.5], [[1, 0], [0, 1]], [[1, -1], [-1, 1]], 1.1)
        self.assertAlmostEqual(r["evsi"], 1.0); self.assertEqual(r["recommendation"], "DO_NOT_MEASURE")
    def test_information_can_be_irrelevant_to_decision(self):
        r = expected_value_of_sample_information([0.5, 0.5], [[1, 0], [0, 1]], [[1, 1], [0, 0]], 0.0)
        self.assertAlmostEqual(r["information_gain_nats"], math.log(2)); self.assertAlmostEqual(r["evsi"], 0.0)
    def test_rejects_unnormalized_prior(self):
        with self.assertRaises(ValueError): information_gain([0.2, 0.2], [[1, 0], [0, 1]])
    def test_rejects_bad_likelihood_dimensions(self):
        with self.assertRaises(ValueError): information_gain([0.5, 0.5], [[1, 0], [1, 0, 0]])
    def test_rejects_negative_cost(self):
        with self.assertRaises(ValueError):
            expected_value_of_sample_information([0.5, 0.5], [[1, 0], [0, 1]], [[1, -1], [-1, 1]], -1)

if __name__ == "__main__":
    unittest.main()
