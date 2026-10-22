import unittest
from cxlvi_minimal_behavioral_quotient import minimal_behavioral_quotient, verify_quotient


class MinimalBehavioralQuotientTests(unittest.TestCase):
    def test_delayed_distinction_forces_split(self):
        states = ("x", "y", "x1", "y1", "good", "bad")
        edges = {("x", "go"): "x1", ("y", "go"): "y1",
                 ("x1", "go"): "good", ("y1", "go"): "bad"}
        step = lambda s, a: edges.get((s, a), s)
        obs = lambda s: "same" if s in ("x", "y", "x1", "y1") else s
        result = minimal_behavioral_quotient(states, ("go",), step, obs)
        self.assertNotEqual(next(i for i,b in enumerate(result.blocks) if "x" in b),
                            next(i for i,b in enumerate(result.blocks) if "y" in b))
        self.assertTrue(verify_quotient(result, ("go",), step, obs))

    def test_behaviorally_identical_states_are_merged(self):
        result = minimal_behavioral_quotient(("a", "b"), ("go",),
            lambda s, _a: s, lambda _s: "same")
        self.assertEqual(result.quotient_state_count, 1)
        self.assertEqual(result.reductions, 1)

    def test_action_availability_splits_states(self):
        result = minimal_behavioral_quotient(("x", "y"), ("go",),
            lambda s, _a: s, lambda _s: "same", enabled=lambda s, _a: s == "x")
        self.assertEqual(result.quotient_state_count, 2)

    def test_terminal_behavior_splits_states(self):
        result = minimal_behavioral_quotient(("x", "y"), ("go",),
            lambda s, _a: None if s == "x" else "y", lambda _s: "same")
        self.assertEqual(result.quotient_state_count, 2)

    def test_duplicate_states_rejected(self):
        with self.assertRaises(ValueError):
            minimal_behavioral_quotient(("x", "x"), (), lambda s, _a: s, lambda s: s)

    def test_external_successor_rejected(self):
        with self.assertRaises(ValueError):
            minimal_behavioral_quotient(("x",), ("go",), lambda _s, _a: "outside", lambda _s: 0)


if __name__ == "__main__":
    unittest.main()
