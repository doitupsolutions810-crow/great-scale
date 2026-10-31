import unittest
from cxliv_transition_preserving_state import audit_transition_congruence


class TransitionPreservingStateTests(unittest.TestCase):
    def test_safe_merge(self):
        states = ("a0", "b0", "a1", "b1")
        key = lambda s: s[1]
        def step(s, action):
            return ("a1" if s[0] == "a" else "b1") if action == "go" else s
        report = audit_transition_congruence(
            states, ("go",), key, step, observation=lambda _s: "same")
        self.assertTrue(report.preserves_quotient, report.violations)
        self.assertEqual(report.equivalent_pairs_checked, 2)

    def test_divergent_successor_is_rejected(self):
        states = ("left", "right", "doneA", "doneB")
        key = lambda s: "start" if s in ("left", "right") else s
        def step(s, action):
            return {"left": "doneA", "right": "doneB"}.get(s, s) if action == "go" else s
        report = audit_transition_congruence(
            states, ("go",), key, step,
            observation=lambda s: "current" if s in ("left", "right") else s)
        self.assertFalse(report.preserves_quotient)
        self.assertTrue(any(v.kind == "successor_key_mismatch" for v in report.violations))

    def test_enabled_action_mismatch_is_rejected(self):
        report = audit_transition_congruence(
            ("x", "y"), ("go",), lambda _s: 0, lambda s, _a: s,
            observation=lambda _s: 0, enabled=lambda s, _a: s == "x")
        self.assertTrue(any(v.kind == "enabled_action_mismatch" for v in report.violations))

    def test_terminal_mismatch_is_rejected(self):
        report = audit_transition_congruence(
            ("x", "y"), ("go",), lambda _s: 0,
            lambda s, _a: None if s == "x" else "y",
            observation=lambda _s: 0)
        self.assertTrue(any(v.kind == "terminal_mismatch" for v in report.violations))

    def test_distinct_keys_are_not_compared(self):
        report = audit_transition_congruence(
            ("x", "y"), ("go",), lambda s: s, lambda s, _a: s,
            observation=lambda s: s)
        self.assertEqual(report.equivalent_pairs_checked, 0)
        self.assertTrue(report.preserves_quotient)


if __name__ == "__main__":
    unittest.main()
