import unittest
from validation_leakage import assess_validation_independence, grouped_evidence_effective_sample_size, admission_with_independence

class ValidationLeakageTests(unittest.TestCase):
    def test_overlapping_sources_detected(self):
        r=assess_validation_independence(["data-A","data-B"],["data-B","holdout-C"])
        self.assertEqual(r["status"],"DEPENDENCE_RISK_DETECTED")
        self.assertEqual(r["overlapping_sources"],["data-B"])
    def test_shared_preprocessing_detected(self):
        r=assess_validation_independence(["train"],["test"],shared_preprocessing=True)
        self.assertIn("SHARED_PREPROCESSING",r["risk_flags"])
    def test_shared_selection_rule_detected(self):
        r=assess_validation_independence(["train"],["test"],shared_selection_rule=True)
        self.assertIn("SHARED_SELECTION_RULE",r["risk_flags"])
    def test_no_recorded_overlap_not_proof(self):
        r=assess_validation_independence(["train"],["external"])
        self.assertEqual(r["status"],"NO_RECORDED_OVERLAP_REQUIRES_EXTERNAL_REVIEW")
        self.assertIn("not proof",r["warning"])
    def test_group_count_diagnostic(self):
        r=grouped_evidence_effective_sample_size(["a","a","a","b","b","c"])
        self.assertEqual(r["observations"],6)
        self.assertEqual(r["independent_groups"],3)
        self.assertEqual(r["group_fraction"],.5)
    def test_empty_group_ids_rejected(self):
        with self.assertRaises(ValueError): grouped_evidence_effective_sample_size([])
    def test_admission_blocked_by_overlap(self):
        c={"model_id":"m","assumptions":["x"],"construction_rationale":"r","evidence_reference":"e","independent_validation_passed":True}
        report=assess_validation_independence(["same"],["same"])
        self.assertFalse(admission_with_independence(c,report)["admit"])
    def test_admission_requires_validation_flag(self):
        c={"model_id":"m","assumptions":["x"],"construction_rationale":"r","evidence_reference":"e"}
        report=assess_validation_independence(["train"],["external"])
        self.assertEqual(admission_with_independence(c,report)["status"],"INDEPENDENT_VALIDATION_NOT_CONFIRMED")
    def test_admission_only_eligible_pending_domain_review(self):
        c={"model_id":"m","assumptions":["x"],"construction_rationale":"r","evidence_reference":"e","independent_validation_passed":True}
        report=assess_validation_independence(["train"],["external"])
        self.assertEqual(admission_with_independence(c,report)["status"],"ELIGIBLE_PENDING_DOMAIN_REVIEW")

if __name__=="__main__": unittest.main()
