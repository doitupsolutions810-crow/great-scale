import unittest
from evidence_gated_admission import assess_candidate, decision_stability

class EvidenceGatedAdmissionTests(unittest.TestCase):
    def complete(self, **extra):
        c={"model_id":"C","assumptions":["stated assumption"],"construction_rationale":"constructed to test failure mode","evidence_reference":"record-1"}
        c.update(extra)
        return c
    def test_incomplete_candidate_not_admitted(self):
        r=assess_candidate({"model_id":"C"})
        self.assertEqual(r["status"],"INCOMPLETE")
        self.assertFalse(r["admit_to_plausible_set"])
    def test_unvalidated_candidate_can_be_stress_tested(self):
        r=assess_candidate(self.complete())
        self.assertEqual(r["status"],"PENDING_INDEPENDENT_VALIDATION")
        self.assertTrue(r["stress_test"])
        self.assertFalse(r["admit_to_plausible_set"])
    def test_independently_validated_candidate_eligible(self):
        r=assess_candidate(self.complete(independent_validation_passed=True))
        self.assertEqual(r["status"],"ELIGIBLE_FOR_PLAUSIBLE_SET_ADMISSION")
        self.assertTrue(r["admit_to_plausible_set"])
    def test_contradicted_candidate_not_admitted(self):
        r=assess_candidate(self.complete(contradicted_by_validation=True))
        self.assertEqual(r["status"],"REJECTED_FOR_CURRENT_EVIDENCE")
        self.assertTrue(r["stress_test"])
        self.assertFalse(r["admit_to_plausible_set"])
    def test_decision_flip_from_xciv(self):
        r=decision_stability({"A":.8,"B":.6},"C",-.1)
        self.assertEqual(r["decision_before"],"ACCEPT")
        self.assertEqual(r["decision_after"],"NOT_CERTIFIED")
        self.assertTrue(r["decision_changed"])
    def test_positive_candidate_does_not_raise_worst_case(self):
        r=decision_stability({"A":.8,"B":.6},"C",.7)
        self.assertAlmostEqual(r["expanded_worst_case"],.6)
        self.assertFalse(r["decision_changed"])
    def test_empty_current_set_rejected(self):
        with self.assertRaises(ValueError): decision_stability({},"C",-.1)
    def test_nonfinite_score_rejected(self):
        with self.assertRaises(ValueError): decision_stability({"A":.5},"C",float("inf"))
    def test_missing_provenance_is_listed(self):
        r=assess_candidate({"model_id":"C","assumptions":["x"],"construction_rationale":"why"})
        self.assertIn("evidence_reference",r["missing_fields"])

if __name__=="__main__": unittest.main()
