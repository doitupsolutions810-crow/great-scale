import unittest
from hidden_common_causes import posterior_probability, assess_candidate

class HiddenCauseTests(unittest.TestCase):
    def test_bayes_update(self):
        self.assertAlmostEqual(posterior_probability(0.2, 4.0), 0.5)

    def test_zero_likelihood_ratio(self):
        self.assertEqual(posterior_probability(0.2, 0.0), 0.0)

    def test_independent_validation_can_pass_gate(self):
        a = assess_candidate("shared-calibration", 0.1, 8.0, 5.0, True, 3.0)
        self.assertTrue(a.accepted_for_model_update)
        self.assertEqual(a.disposition, "ELIGIBLE_FOR_REVIEW_NOT_AUTOMATICALLY_CAUSAL")

    def test_discovery_fit_does_not_replace_validation(self):
        a = assess_candidate("candidate", 0.1, 100.0, 1.1, True, 3.0)
        self.assertFalse(a.accepted_for_model_update)

    def test_reused_discovery_data_blocked(self):
        a = assess_candidate("candidate", 0.1, 100.0, 20.0, False, 3.0)
        self.assertFalse(a.accepted_for_model_update)
        self.assertEqual(a.disposition, "HOLDOUT_NOT_INDEPENDENT")

    def test_invalid_prior_rejected(self):
        with self.assertRaises(ValueError):
            posterior_probability(1.0, 2.0)

if __name__ == "__main__":
    unittest.main()
