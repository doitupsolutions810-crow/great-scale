import unittest
from cxlix_joint_behavioral_property_fixed_point import joint_refinement


class JointFixedPointTests(unittest.TestCase):
    def test_splits_hidden_unsafe_state_and_keeps_transition_consistency(self):
        states = ("safe", "unsafe", "end")
        transitions = {"safe": {"go": "end"}, "unsafe": {"go": "end"}, "end": {}}
        observations = {"safe": "idle", "unsafe": "idle", "end": "done"}
        report = joint_refinement(states, transitions, observations, (lambda s: s == "unsafe",))
        self.assertTrue(report.stable)
        self.assertTrue(report.properties_preserved)
        self.assertTrue(report.transition_consistent)
        self.assertEqual(report.final_block_count, 3)

    def test_distinguishes_successors_that_split_later(self):
        states = ("x", "y", "good", "bad")
        transitions = {"x": {"step": "good"}, "y": {"step": "bad"},
                       "good": {}, "bad": {}}
        observations = {"x": "start", "y": "start", "good": "result", "bad": "result"}
        props = (lambda s: s == "bad",)
        report = joint_refinement(states, transitions, observations, props)
        self.assertTrue(report.transition_consistent)
        self.assertTrue(report.properties_preserved)
        self.assertNotEqual(next(i for i,b in enumerate(report.blocks) if "x" in b),
                            next(i for i,b in enumerate(report.blocks) if "y" in b))

    def test_same_behavior_and_property_merge(self):
        states = ("a", "b", "end")
        transitions = {"a": {"go": "end"}, "b": {"go": "end"}, "end": {}}
        observations = {"a": "start", "b": "start", "end": "finish"}
        report = joint_refinement(states, transitions, observations, (lambda s: s == "end",))
        self.assertEqual(report.final_block_count, 2)
        self.assertTrue(report.transition_consistent)

    def test_enabled_action_difference_splits(self):
        states = ("a", "b")
        transitions = {"a": {"go": "a"}, "b": {}}
        observations = {"a": "same", "b": "same"}
        report = joint_refinement(states, transitions, observations, ())
        self.assertEqual(report.final_block_count, 2)

    def test_out_of_domain_successor_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside states"):
            joint_refinement(("a",), {"a": {"go": "missing"}}, {"a": "x"}, ())

    def test_incomplete_observation_map_rejected(self):
        with self.assertRaisesRegex(ValueError, "cover exactly"):
            joint_refinement(("a", "b"), {"a": {}, "b": {}}, {"a": "x"}, ())


if __name__ == "__main__":
    unittest.main()
