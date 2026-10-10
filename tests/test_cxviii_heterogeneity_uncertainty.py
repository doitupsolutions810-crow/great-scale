import unittest
from cxviii_heterogeneity_uncertainty import analyze_heterogeneity

def rows(cid, pairs):
    return [{"cluster_id": cid, "a": a, "b": b} for a, b in pairs]

class TestCXVIII(unittest.TestCase):
    def fixture(self):
        data = []
        for i in range(6):
            data += rows(f"ind-{i}", [(0,0),(0,1),(1,0),(1,1)])
        for i in range(6):
            data += rows(f"dep-{i}", [(0,0),(1,1)])
        return data

    def test_cluster_estimates_and_mean(self):
        r = analyze_heterogeneity(self.fixture(), reps=500, seed=7)
        self.assertEqual(r["n_clusters"], 12)
        self.assertAlmostEqual(r["cluster_excess"]["ind-0"], 0.0)
        self.assertAlmostEqual(r["cluster_excess"]["dep-0"], 0.25)
        self.assertAlmostEqual(r["equal_cluster_mean_excess"], 0.125)
        self.assertAlmostEqual(r["min_cluster_excess"], 0.0)
        self.assertAlmostEqual(r["max_cluster_excess"], 0.25)
        self.assertIsNotNone(r["interval"])

    def test_seed_reproducibility(self):
        a = analyze_heterogeneity(self.fixture(), reps=500, seed=11)
        b = analyze_heterogeneity(self.fixture(), reps=500, seed=11)
        self.assertEqual(a["interval"], b["interval"])

    def test_insufficient_clusters(self):
        r = analyze_heterogeneity(rows("one", [(0,0),(1,1)]))
        self.assertEqual(r["status"], "INSUFFICIENT_CLUSTERS")
        self.assertIsNone(r["interval"])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            analyze_heterogeneity([{"cluster_id":"x","a":2,"b":0}])
        with self.assertRaises(ValueError):
            analyze_heterogeneity([{"cluster_id":"x","a":0,"b":0}], reps=10)
        with self.assertRaises(ValueError):
            analyze_heterogeneity([{"cluster_id":"","a":0,"b":0}])
        with self.assertRaises(ValueError):
            analyze_heterogeneity([{"cluster_id":"x","a":0,"b":0}], alpha=1.0)

    def test_equal_size_fixture_estimands(self):
        r = analyze_heterogeneity(self.fixture(), reps=500, seed=2)
        self.assertAlmostEqual(r["trial_weighted_pooled_excess"], 0.125)

if __name__ == "__main__":
    unittest.main()
