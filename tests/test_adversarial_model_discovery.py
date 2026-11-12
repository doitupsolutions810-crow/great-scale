import unittest
from adversarial_model_discovery import decision_from_values, evaluate_model_expansion, classify_candidate

class AdversarialDiscoveryTests(unittest.TestCase):
    def test_empty_set_rejected(self):
        with self.assertRaises(ValueError): decision_from_values({})
    def test_positive_set_accepts(self):
        self.assertEqual(decision_from_values({"A": .8, "B": .6}), "ACCEPT")
    def test_negative_candidate_flips_decision(self):
        r = evaluate_model_expansion({"A": .8, "B": .6}, {"C": -.1})
        self.assertEqual(r["decision_before"], "ACCEPT")
        self.assertEqual(r["decision_after"], "NOT_CERTIFIED")
        self.assertTrue(r["decision_changed"])
        self.assertAlmostEqual(r["expanded_worst_case"], -.1)
    def test_benign_candidate_cannot_raise_worst_case(self):
        r = evaluate_model_expansion({"A": .8, "B": .6}, {"C": .7})
        self.assertAlmostEqual(r["expanded_worst_case"], .6)
        self.assertTrue(r["monotonicity_holds"])
    def test_existing_model_cannot_be_silently_changed(self):
        with self.assertRaises(ValueError): evaluate_model_expansion({"A": .8}, {"A": .2})
    def test_incomplete_candidate_flagged(self):
        self.assertEqual(classify_candidate({"model_id":"C"})["status"], "INCOMPLETE_CANDIDATE")
    def test_hypothesis_not_mistaken_for_evidence(self):
        c = {"model_id":"C","assumptions":["x"],"construction_rationale":"counterexample","evidence_reference":"lab-note-1","empirically_supported":False}
        self.assertEqual(classify_candidate(c)["status"], "HYPOTHETICAL_CANDIDATE_REQUIRES_EVIDENCE")
    def test_evidence_backed_still_requires_validation(self):
        c = {"model_id":"C","assumptions":["x"],"construction_rationale":"counterexample","evidence_reference":"dataset-2","empirically_supported":True}
        self.assertEqual(classify_candidate(c)["status"], "EVIDENCE_BACKED_CANDIDATE_REQUIRES_VALIDATION")
    def test_nonfinite_value_rejected(self):
        with self.assertRaises(ValueError): decision_from_values({"A": float("inf")})

if __name__ == "__main__": unittest.main()
