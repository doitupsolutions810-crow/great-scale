import unittest
from great_scale.observation import certify_side

class ObservationCertificateTests(unittest.TestCase):
    def test_certifies_above_when_gap_exceeds_bound(self):
        result = certify_side(1.20, 1.00, 0.10)
        self.assertTrue(result.certified)
        self.assertEqual(result.certified_side, 1)
        self.assertAlmostEqual(result.margin, 0.10)

    def test_certifies_below_when_gap_exceeds_bound(self):
        result = certify_side(0.80, 1.00, 0.10)
        self.assertTrue(result.certified)
        self.assertEqual(result.certified_side, -1)

    def test_uncertainty_interval_overlaps_reference(self):
        result = certify_side(1.05, 1.00, 0.10)
        self.assertFalse(result.certified)
        self.assertEqual(result.certified_side, 0)

    def test_boundary_is_inconclusive(self):
        result = certify_side(1.5, 1.0, 0.5)
        self.assertFalse(result.certified)
        self.assertEqual(result.certified_side, 0)

    def test_negative_error_bound_is_rejected(self):
        with self.assertRaises(ValueError):
            certify_side(1.2, 1.0, -0.1)

if __name__ == "__main__":
    unittest.main()
