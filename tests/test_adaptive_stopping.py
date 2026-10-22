import unittest
from great_scale.adaptive_stopping import first_certified_observation, planned_minimum_n

class AdaptiveStoppingTests(unittest.TestCase):
    def test_stops_at_first_certified_observation(self):
        result = first_certified_observation([(1.02, 0.05), (1.20, 0.10), (1.30, 0.05)], 1.0)
        self.assertTrue(result.stopped)
        self.assertEqual(result.stop_index, 1)
        self.assertEqual(result.certified_side, 1)

    def test_reports_below_side(self):
        result = first_certified_observation([(0.7, 0.1)], 1.0)
        self.assertTrue(result.stopped)
        self.assertEqual(result.certified_side, -1)

    def test_no_certificate_remains_unresolved(self):
        result = first_certified_observation([(1.05, 0.1), (1.04, 0.05)], 1.0)
        self.assertFalse(result.stopped)
        self.assertEqual(result.certified_side, 0)

    def test_empty_sequence_is_unresolved(self):
        result = first_certified_observation([], 1.0)
        self.assertFalse(result.stopped)
        self.assertIsNone(result.stop_index)

    def test_bias_floor_can_make_certification_impossible(self):
        self.assertIsNone(planned_minimum_n(0.05, 0.05, 0.2))
        self.assertIsNone(planned_minimum_n(0.04, 0.05, 0.2))

    def test_planned_sample_count_respects_strict_boundary(self):
        self.assertEqual(planned_minimum_n(0.2, 0.1, 0.2), 5)
        self.assertEqual(planned_minimum_n(0.2, 0.1, 0), 1)

    def test_rejects_invalid_bounds(self):
        with self.assertRaises(ValueError):
            planned_minimum_n(0.1, -0.01, 0.2)
        with self.assertRaises(ValueError):
            first_certified_observation([(1.1, -0.1)], 1.0)

if __name__ == "__main__":
    unittest.main()
