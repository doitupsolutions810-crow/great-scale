import math
import unittest
from sequential_stopping import (
    audit_stopping_rule, bernoulli_e_process, evidence_threshold,
    independent_bernoulli_log_lr, stopping_decision,
)


class SequentialStoppingTests(unittest.TestCase):
    def test_likelihood_ratio_for_one_success(self):
        self.assertAlmostEqual(independent_bernoulli_log_lr([1], 0.5, 0.8), math.log(1.6))

    def test_e_value_matches_likelihood_ratio(self):
        self.assertAlmostEqual(bernoulli_e_process([1, 1], 0.5, 0.8), 2.56)

    def test_threshold_for_five_percent(self):
        self.assertEqual(evidence_threshold(0.05), 20)

    def test_below_threshold_continues(self):
        self.assertEqual(stopping_decision(19.99, 0.05), "CONTINUE_OR_INCONCLUSIVE")

    def test_at_threshold_rejects(self):
        self.assertEqual(stopping_decision(20, 0.05), "EVIDENCE_THRESHOLD_REACHED")

    def test_rejects_empty_observations(self):
        with self.assertRaises(ValueError):
            bernoulli_e_process([], 0.5, 0.8)

    def test_rejects_invalid_observation(self):
        with self.assertRaises(ValueError):
            independent_bernoulli_log_lr([2], 0.5, 0.8)

    def test_rejects_equal_hypotheses(self):
        with self.assertRaises(ValueError):
            bernoulli_e_process([1], 0.5, 0.5)

    def test_audit_fixed_alpha_and_increasing_looks(self):
        result = audit_stopping_rule([
            {"look": 1, "alpha": 0.05, "stopped": False},
            {"look": 2, "alpha": 0.05, "stopped": True},
        ])
        self.assertTrue(result["valid_log"])
        self.assertEqual(result["stopped_at"], 2)

    def test_audit_detects_alpha_drift_and_post_stop_look(self):
        result = audit_stopping_rule([
            {"look": 1, "alpha": 0.05, "stopped": True},
            {"look": 2, "alpha": 0.10, "stopped": False},
        ])
        self.assertFalse(result["valid_log"])
        self.assertTrue(any("alpha changed" in issue for issue in result["issues"]))
        self.assertTrue(any("after a stop" in issue for issue in result["issues"]))


if __name__ == "__main__":
    unittest.main()
