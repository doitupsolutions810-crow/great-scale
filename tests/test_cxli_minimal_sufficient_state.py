import itertools
import unittest

from cxli_minimal_sufficient_state import audit_state_sufficiency, adaptive_key


class MinimalSufficientStateTests(unittest.TestCase):
    def test_homogeneous_effects_count_key_is_sufficient(self):
        assignments = list(itertools.product(("A", "B"), repeat=3))
        effects = {"A": (0.0, 0.1), "B": (0.4, 0.5)}
        report = audit_state_sufficiency(
            assignments,
            state_key=lambda x: tuple(sorted((c, x.count(c)) for c in set(x))),
            outcome_signature=lambda x: (
                sum(effects[c][0] for c in x),
                sum(effects[c][1] for c in x),
            ),
        )
        self.assertTrue(report.sufficient)
        self.assertEqual(report.assignment_count, 8)
        self.assertEqual(report.compressed_state_count, 4)

    def test_heterogeneous_effects_break_count_only_state(self):
        assignments = [("A", "B"), ("B", "A")]
        effects = (
            {"A": (0.0, 0.1), "B": (0.4, 0.5)},
            {"A": (0.2, 0.3), "B": (0.8, 0.9)},
        )
        count_only = audit_state_sufficiency(
            assignments,
            state_key=lambda x: tuple(sorted((c, x.count(c)) for c in set(x))),
            outcome_signature=lambda x: tuple(
                round(sum(effects[i][c][bound] for i, c in enumerate(x)), 12)
                for bound in (0, 1)
            ),
        )
        self.assertFalse(count_only.sufficient)
        self.assertEqual(len(count_only.collisions), 1)
        self.assertEqual(count_only.collisions[0].first_signature, (0.8, 1.0))
        self.assertEqual(count_only.collisions[0].second_signature, (0.6, 0.8))

    def test_refined_key_separates_heterogeneous_assignments(self):
        assignments = [("A", "B"), ("B", "A")]
        effects = (
            {"A": (0.0, 0.1), "B": (0.4, 0.5)},
            {"A": (0.2, 0.3), "B": (0.8, 0.9)},
        )
        report = audit_state_sufficiency(
            assignments,
            state_key=lambda x: adaptive_key(x, effects),
            outcome_signature=lambda x: tuple(
                round(sum(effects[i][c][bound] for i, c in enumerate(x)), 12)
                for bound in (0, 1)
            ),
        )
        self.assertTrue(report.sufficient)
        self.assertEqual(report.compressed_state_count, 2)

    def test_feasibility_must_be_part_of_outcome_signature(self):
        assignments = ("left", "right")
        report = audit_state_sufficiency(
            assignments,
            state_key=lambda _: "same-state",
            outcome_signature=lambda x: x == "left",
        )
        self.assertFalse(report.sufficient)


if __name__ == "__main__":
    unittest.main()
