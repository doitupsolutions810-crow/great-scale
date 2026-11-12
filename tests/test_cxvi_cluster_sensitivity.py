import unittest
from cxvi_cluster_sensitivity import analyze_cluster_sensitivity

def make_trials(cluster_sizes):
    rows = []
    for ci, size in enumerate(cluster_sizes):
        for j in range(size):
            a = (j % 4) < 2
            b = ((j % 4) < 2) if ci % 2 == 0 else ((j % 4) >= 2)
            rows.append({"cluster_id": f"c{ci}", "a_failed": bool(a), "b_failed": bool(b)})
    return rows

class ClusterSensitivityTests(unittest.TestCase):
    def test_cluster_sizes_and_icc_grid(self):
        result = analyze_cluster_sensitivity(make_trials([4, 4, 8, 8]),
            icc_values=[0, .2, 1], bootstrap_replicates=200,
            min_clusters=2, min_trials=2, seed=7)
        self.assertEqual(result["n_clusters"], 4)
        self.assertEqual(result["cluster_size_summary"]["minimum"], 4)
        self.assertEqual(result["cluster_size_summary"]["maximum"], 8)
        scenarios = result["design_effect_sensitivity"]
        self.assertEqual([x["assumed_icc"] for x in scenarios], [0., .2, 1.])
        self.assertAlmostEqual(scenarios[0]["effective_sample_size_approx"], 24)
        self.assertGreater(scenarios[0]["effective_sample_size_approx"], scenarios[1]["effective_sample_size_approx"])
        self.assertGreater(scenarios[1]["effective_sample_size_approx"], scenarios[2]["effective_sample_size_approx"])

    def test_invalid_icc_rejected(self):
        with self.assertRaises(ValueError):
            analyze_cluster_sensitivity(make_trials([2, 2]), icc_values=[-0.1],
                bootstrap_replicates=100, min_clusters=2, min_trials=2)

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            analyze_cluster_sensitivity([])

    def test_reproducible_bootstrap(self):
        kwargs = dict(icc_values=[0, .25, .5], bootstrap_replicates=200,
            min_clusters=2, min_trials=2, seed=11)
        a = analyze_cluster_sensitivity(make_trials([4, 4, 4, 4]), **kwargs)
        b = analyze_cluster_sensitivity(make_trials([4, 4, 4, 4]), **kwargs)
        self.assertEqual(a, b)

if __name__ == "__main__":
    unittest.main()
