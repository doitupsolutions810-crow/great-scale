import unittest
from evidence_independence import audit_declared_sources, effective_sample_size, mean_error_variance

class EvidenceIndependenceTests(unittest.TestCase):
    def test_shared_source_flagged(self):
        a = audit_declared_sources([["sensor-A", "cal-7"], ["lab-B", "cal-7"]])
        self.assertEqual(a.status, "SHARED_CAUSE_CANDIDATE")
        self.assertEqual(a.shared_sources, ("cal-7",))
    def test_no_overlap_does_not_claim_independence(self):
        a = audit_declared_sources([["sensor-A"], ["lab-B"]])
        self.assertEqual(a.status, "NO_DECLARED_OVERLAP")
        self.assertIn("unproven", a.note)
    def test_requires_two_streams(self):
        with self.assertRaises(ValueError): audit_declared_sources([["one"]])
    def test_correlated_variance(self):
        self.assertAlmostEqual(mean_error_variance(1.0, 10, 0.2), 0.28)
    def test_independent_variance(self):
        self.assertAlmostEqual(mean_error_variance(4.0, 8, 0.0), 0.5)
    def test_effective_sample_size(self):
        self.assertAlmostEqual(effective_sample_size(10, 0.2), 10 / 2.8)
    def test_perfect_correlation(self):
        self.assertAlmostEqual(effective_sample_size(12, 1.0), 1.0)
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): mean_error_variance(1, 0, 0)
        with self.assertRaises(ValueError): mean_error_variance(1, 4, 1.1)

if __name__ == "__main__": unittest.main()
