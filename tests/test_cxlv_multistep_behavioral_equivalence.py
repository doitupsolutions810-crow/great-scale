import unittest
from cxlv_multistep_behavioral_equivalence import compare_through_horizon, refine_behavioral_partition


class MultiStepBehaviorTests(unittest.TestCase):
    def test_divergence_appears_after_two_steps(self):
        transitions = {("x", "go"): "x1", ("y", "go"): "y1",
                      ("x1", "go"): "good", ("y1", "go"): "bad"}
        step = lambda s, a: transitions.get((s, a), s)
        obs = lambda s: "same" if s in ("x", "y", "x1", "y1") else s
        self.assertTrue(compare_through_horizon("x", "y", ("go",), step, obs, horizon=1).equivalent)
        report = compare_through_horizon("x", "y", ("go",), step, obs, horizon=2)
        self.assertFalse(report.equivalent)
        self.assertEqual(report.reason, "observation_mismatch")

    def test_action_availability_distinguishes(self):
        report = compare_through_horizon("x", "y", ("go",), lambda s, _a: s,
            lambda _s: "same", enabled=lambda s, _a: s == "x", horizon=1)
        self.assertEqual(report.reason, "enabled_action_mismatch")

    def test_partition_refinement_splits_future_distinction(self):
        states = ("x", "y", "good", "bad")
        step = lambda s, a: ({"x": "good", "y": "bad"}.get(s, s) if a == "go" else s)
        obs = lambda s: "start" if s in ("x", "y") else s
        blocks = refine_behavioral_partition(states, ("go",), step, obs)
        self.assertFalse(any({"x", "y"}.issubset(set(block)) for block in blocks))

    def test_equivalent_self_loops_remain_grouped(self):
        blocks = refine_behavioral_partition(("a", "b"), ("go",),
            lambda s, _a: s, lambda _s: "same")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(set(blocks[0]), {"a", "b"})

    def test_negative_horizon_rejected(self):
        with self.assertRaises(ValueError):
            compare_through_horizon(1, 2, (), lambda s, _a: s, lambda s: s, horizon=-1)


if __name__ == "__main__":
    unittest.main()
