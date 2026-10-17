import unittest

from cxlx_model_change_robustness import (
    audit_incremental_against_full,
    full_recompute,
    incremental_refine,
    partition_signature,
)


class ModelChangeRobustnessTests(unittest.TestCase):
    def setUp(self):
        self.states = ["a", "b", "c"]
        self.obs = {"a": "x", "b": "x", "c": "y"}
        self.props = {"a": (False,), "b": (False,), "c": (True,)}
        self.edges = {"a": {"go": "c"}, "b": {"go": "c"}, "c": {}}

    def test_incremental_matches_full_after_edge_change(self):
        old = full_recompute(self.states, self.obs, self.props, self.edges)
        changed = {**self.edges, "b": {"go": "b"}}
        report = audit_incremental_against_full(self.states, self.obs, self.props, changed, old)
        self.assertTrue(report["equivalent"])
        self.assertEqual(report["incremental_block_count"], 3)

    def test_added_state_is_included_and_refined(self):
        old = full_recompute(self.states, self.obs, self.props, self.edges)
        states = self.states + ["d"]
        obs = {**self.obs, "d": "x"}
        props = {**self.props, "d": (False,)}
        edges = {**self.edges, "d": {"go": "c"}}
        inc = incremental_refine(states, obs, props, edges, old)
        full = full_recompute(states, obs, props, edges)
        self.assertEqual(partition_signature(inc), partition_signature(full))

    def test_property_change_splits_prior_block(self):
        old = full_recompute(self.states, self.obs, self.props, self.edges)
        props = {**self.props, "b": (True,)}
        inc = incremental_refine(self.states, self.obs, props, self.edges, old)
        self.assertEqual(partition_signature(inc), partition_signature(
            full_recompute(self.states, self.obs, props, self.edges)))

    def test_observation_change_splits_prior_block(self):
        old = full_recompute(self.states, self.obs, self.props, self.edges)
        obs = {**self.obs, "b": "new"}
        self.assertEqual(partition_signature(incremental_refine(
            self.states, obs, self.props, self.edges, old)),
            partition_signature(full_recompute(self.states, obs, self.props, self.edges)))

    def test_old_distinctions_are_not_silently_merged(self):
        prior = [["a"], ["b"], ["c"]]
        inc = incremental_refine(self.states, self.obs, self.props, self.edges, prior)
        self.assertEqual(len(inc), 3)

    def test_invalid_new_successor_rejected(self):
        edges = {**self.edges, "b": {"go": "missing"}}
        with self.assertRaises(ValueError):
            full_recompute(self.states, self.obs, self.props, edges)


if __name__ == "__main__":
    unittest.main()
