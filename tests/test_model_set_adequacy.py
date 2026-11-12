import unittest
from model_set_adequacy import assess_model_set_adequacy, omission_adjusted_lower_bound, REQUIRED_ADEQUACY_FIELDS

class ModelSetAdequacyTests(unittest.TestCase):
    def test_empty_checklist_is_not_adequate(self):
        r = assess_model_set_adequacy({})
        self.assertEqual(r["status"], "ADEQUACY_NOT_ESTABLISHED")
        self.assertEqual(len(r["missing_fields"]), len(REQUIRED_ADEQUACY_FIELDS))
    def test_all_steps_complete_still_requires_justification(self):
        r = assess_model_set_adequacy({k: True for k in REQUIRED_ADEQUACY_FIELDS})
        self.assertEqual(r["status"], "CHECKLIST_COMPLETE_REQUIRES_JUSTIFICATION")
    def test_false_item_blocks_completion(self):
        evidence = {k: True for k in REQUIRED_ADEQUACY_FIELDS}
        evidence["failure_modes_reviewed"] = False
        self.assertEqual(assess_model_set_adequacy(evidence)["status"], "ADEQUACY_NOT_ESTABLISHED")
    def test_omission_bound_example(self):
        r = omission_adjusted_lower_bound(0.6, 0.1, -1.0)
        self.assertAlmostEqual(r["omission_adjusted_lower_bound"], 0.44)
        self.assertEqual(r["recommendation"], "MEASURE_UNDER_STATED_BOUND")
    def test_omitted_mass_can_reverse_decision(self):
        r = omission_adjusted_lower_bound(0.2, 0.5, -1.0)
        self.assertAlmostEqual(r["omission_adjusted_lower_bound"], -0.4)
        self.assertEqual(r["recommendation"], "NOT_CERTIFIED_BY_BOUND")
    def test_rejects_invalid_mass(self):
        with self.assertRaises(ValueError): omission_adjusted_lower_bound(0.5, 1.2, -1.0)
    def test_rejects_unjustified_lower_bound_order(self):
        with self.assertRaises(ValueError): omission_adjusted_lower_bound(0.5, 0.1, 0.6)
    def test_rejects_nonfinite_inputs(self):
        with self.assertRaises(ValueError): omission_adjusted_lower_bound(float("nan"), 0.1, -1.0)

if __name__ == "__main__":
    unittest.main()
