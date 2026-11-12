import unittest
from replication_resilience import conclusion_supported, minimal_cut_sets, surviving_paths


class ReplicationResilienceTests(unittest.TestCase):
    def setUp(self):
        self.paths = {
            "A": {"calibration", "sensor-A"},
            "B": {"calibration", "lab-B"},
            "C": {"independent-reference", "sensor-C"},
        }

    def test_shared_failure_compromises_multiple_paths(self):
        self.assertEqual(surviving_paths(self.paths, {"calibration"}), ("C",))

    def test_threshold_support(self):
        self.assertTrue(conclusion_supported(self.paths, {"sensor-A"}, 2))
        self.assertFalse(conclusion_supported(self.paths, {"calibration"}, 2))

    def test_minimal_single_source_cut(self):
        cuts = minimal_cut_sets(self.paths, 2)
        self.assertIn(("calibration",), cuts)

    def test_cut_sets_are_minimal(self):
        paths = {"A": {"x"}, "B": {"y"}, "C": {"z"}}
        cuts = minimal_cut_sets(paths, 2)
        self.assertEqual(cuts, (("x", "y"), ("x", "z"), ("y", "z")))

    def test_bad_threshold_rejected(self):
        with self.assertRaises(ValueError):
            conclusion_supported(self.paths, set(), 0)
        with self.assertRaises(ValueError):
            minimal_cut_sets(self.paths, 4)

    def test_unknown_failed_source_does_not_compromise_declared_paths(self):
        self.assertEqual(surviving_paths(self.paths, {"unknown"}), ("A", "B", "C"))


if __name__ == "__main__":
    unittest.main()
