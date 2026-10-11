import unittest
from cxvii_weighting_sensitivity import analyze_weighting_sensitivity

class WeightingSensitivityTests(unittest.TestCase):
    def test_equal_cluster_and_trial_weighting_can_differ(self):
        rows = []
        # Large cluster: balanced independent outcomes, excess = 0.
        for a, b in [(False, False), (False, True), (True, False), (True, True)] * 25:
            rows.append({"cluster_id": "large", "a_failed": a, "b_failed": b})
        # Small cluster: perfectly concordant outcomes, excess = 0.25.
        for a, b in [(False, False), (True, True)] * 2:
            rows.append({"cluster_id": "small", "a_failed": a, "b_failed": b})
        result = analyze_weighting_sensitivity(rows)
        self.assertAlmostEqual(result["equal_cluster_weighted_mean_excess"], 0.125)
        self.assertNotAlmostEqual(result["trial_weighted_excess"],
                                  result["equal_cluster_weighted_mean_excess"])
        self.assertEqual(result["n_clusters"], 2)

    def test_cluster_stats_exposed(self):
        rows = [
            {"cluster_id": "x", "a_failed": True, "b_failed": True},
            {"cluster_id": "x", "a_failed": False, "b_failed": False},
            {"cluster_id": "y", "a_failed": True, "b_failed": False},
        ]
        result = analyze_weighting_sensitivity(rows)
        self.assertEqual(len(result["cluster_results"]), 2)
        self.assertEqual(result["cluster_size_summary"]["minimum"], 1)
        self.assertEqual(result["cluster_size_summary"]["maximum"], 2)

    def test_invalid_outcomes_rejected(self):
        with self.assertRaises(ValueError):
            analyze_weighting_sensitivity([{"cluster_id": "x", "a_failed": 1, "b_failed": False}])

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            analyze_weighting_sensitivity([])

if __name__ == "__main__":
    unittest.main()
