import unittest
from cxix_informative_cluster_selection import diagnose_cluster_size

def rows(cid, pairs, probability=None):
    out=[]
    for a,b in pairs:
        r={"cluster_id":cid,"a":a,"b":b}
        if probability is not None: r["selection_probability"]=probability
        out.append(r)
    return out

class TestCXIX(unittest.TestCase):
    def fixture(self):
        data=[]
        for i in range(6):
            data += rows(f"small-{i}", [(0,0),(0,1),(1,0),(1,1)])
        for i in range(6):
            data += rows(f"large-{i}", [(0,0),(1,1)]*4)
        return data

    def test_size_association_diagnostic(self):
        r=diagnose_cluster_size(self.fixture())
        self.assertEqual(r["n_clusters"],12)
        self.assertIsNotNone(r["size_excess_pearson_correlation"])
        self.assertEqual(r["selection_status"],"NOT_IDENTIFIABLE_FROM_OBSERVED_CLUSTERS_ALONE")
        self.assertIsNone(r["selection_weighted_mean_excess"])

    def test_selection_weights_require_valid_probabilities(self):
        data=rows("a",[(0,0),(1,1)],0.5)+rows("b",[(0,0),(0,1),(1,0),(1,1)],1.0)
        r=diagnose_cluster_size(data)
        self.assertEqual(r["selection_status"],"PROBABILITIES_SUPPLIED_UNVERIFIED")
        self.assertIsNotNone(r["selection_weighted_mean_excess"])

    def test_invalid_and_inconsistent_probabilities(self):
        with self.assertRaises(ValueError):
            diagnose_cluster_size(rows("a",[(0,0)],0))
        with self.assertRaises(ValueError):
            diagnose_cluster_size(rows("a",[(0,0)],0.5)+rows("a",[(1,1)],0.8))
        with self.assertRaises(ValueError):
            diagnose_cluster_size([{"cluster_id":"x","a":2,"b":0}])

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            diagnose_cluster_size([])

if __name__ == "__main__":
    unittest.main()
