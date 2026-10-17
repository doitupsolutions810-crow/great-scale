import unittest
from cxlxi_canonical_quotient_repair import canonical_quotient, partition_signature, repair_and_audit

class CanonicalQuotientRepairTests(unittest.TestCase):
    def setUp(self):
        self.states = ["a", "b", "c"]
        self.obs = {"a": "same", "b": "same", "c": "other"}
        self.props = {"a": (False,), "b": (False,), "c": (True,)}
        self.edges = {"a": {"go": "c"}, "b": {"go": "c"}, "c": {}}

    def test_coarsest_partition_merges_behaviorally_equal_states(self):
        p = canonical_quotient(self.states, self.obs, self.props, self.edges)
        self.assertEqual(len(p), 2)
        self.assertIn(frozenset({"a", "b"}), p)

    def test_repair_detects_stale_over_split_cache(self):
        report = repair_and_audit(self.states, self.obs, self.props, self.edges, [["a"], ["b"], ["c"]])
        self.assertTrue(report["repair_needed"])
        self.assertEqual(report["canonical_block_count"], 2)

    def test_matching_cache_needs_no_repair(self):
        p = canonical_quotient(self.states, self.obs, self.props, self.edges)
        report = repair_and_audit(self.states, self.obs, self.props, self.edges, p)
        self.assertFalse(report["repair_needed"])
        self.assertTrue(report["cached_matches_canonical"])

    def test_behavior_change_splits_previously_equivalent_states(self):
        edges = {**self.edges, "b": {"go": "b"}}
        self.assertEqual(len(canonical_quotient(self.states, self.obs, self.props, edges)), 3)

    def test_invalid_successor_is_rejected(self):
        edges = {**self.edges, "a": {"go": "missing"}}
        with self.assertRaises(ValueError):
            canonical_quotient(self.states, self.obs, self.props, edges)

    def test_partition_comparison_ignores_block_order(self):
        p = canonical_quotient(self.states, self.obs, self.props, self.edges)
        self.assertEqual(partition_signature(p), partition_signature(list(reversed([list(b) for b in p])))

if __name__ == "__main__":
    unittest.main()
