import unittest

from sequential_validation import (
    audit_model_selection,
    bonferroni_alpha,
    familywise_false_positive_independent,
    validation_set_status,
)


class SequentialValidationTests(unittest.TestCase):
    def test_one_look_matches_per_test_rate(self):
        self.assertAlmostEqual(familywise_false_positive_independent(0.05, 1), 0.05)

    def test_twenty_looks_example(self):
        self.assertAlmostEqual(familywise_false_positive_independent(0.05, 20), 0.6415140776)

    def test_bonferroni_level(self):
        self.assertAlmostEqual(bonferroni_alpha(0.05, 20), 0.0025)

    def test_invalid_look_count(self):
        with self.assertRaises(ValueError):
            bonferroni_alpha(0.05, 0)

    def test_rejects_boolean_as_look_count(self):
        with self.assertRaises(TypeError):
            familywise_false_positive_independent(0.05, True)

    def test_test_use_overrides_other_flags(self):
        self.assertEqual(validation_set_status(1, True, True), "TEST_SET_COMPROMISED")

    def test_untouched_test(self):
        self.assertEqual(validation_set_status(10, False, True), "UNTOUCHED_FINAL_TEST")

    def test_validation_reuse(self):
        self.assertEqual(validation_set_status(3, False, False), "VALIDATION_REUSED")

    def test_audit_detects_test_feedback(self):
        result = audit_model_selection([
            {"look": 1, "dataset_role": "validation", "influenced_decision": True},
            {"look": 2, "dataset_role": "test", "influenced_decision": True},
        ])
        self.assertTrue(result["test_set_compromised"])
        self.assertEqual(result["status"], "TEST_SET_COMPROMISED")

    def test_audit_flags_duplicate_look(self):
        result = audit_model_selection([
            {"look": 1, "dataset_role": "validation", "influenced_decision": False},
            {"look": 1, "dataset_role": "validation", "influenced_decision": False},
        ])
        self.assertTrue(any("duplicate look index" in issue for issue in result["issues"]))


if __name__ == "__main__":
    unittest.main()
