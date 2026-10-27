import itertools
import unittest

from cxlii_coarsest_valid_partition import audit_partition, outcome_key


class CoarsestPartitionTests(unittest.TestCase):
    def test_count_key_is_coarsest_for_homogeneous_additive_outcomes(self):
        assignments = list(itertools.product(("A", "B"), repeat=3))
        effects = {"A": (0, 1), "B": (4, 5)}
        report = audit_partition(
            assignments,
            state_key=lambda x: tuple(sorted((c, x.count(c)) for c in set(x))),
            outcome=lambda x: (sum(effects[c][0] for c in x), sum(effects[c][1] for c in x)),
        )
        self.assertTrue(report.sufficient)
        self.assertTrue(report.coarsest_for_signature)
        self.assertEqual(report.candidate_state_count, 4)
        self.assertEqual(report.oracle_class_count, 4)
        self.assertEqual(report.excess_states, 0)

    def test_count_key_has_collision_for_heterogeneous_effects(self):
        assignments = [("A", "B"), ("B", "A")]
        effects = (
            {"A": (0.0, 0.1), "B": (0.4, 0.5)},
            {"A": (0.2, 0.3), "B": (0.8, 0.9)},
        )
        report = audit_partition(
            assignments,
            state_key=lambda x: tuple(sorted((c, x.count(c)) for c in set(x))),
            outcome=lambda x: tuple(round(sum(effects[i][c][b] for i, c in enumerate(x)), 12) for b in (0, 1)),
        )
        self.assertFalse(report.sufficient)
        self.assertEqual(len(report.collisions), 1)
        self.assertEqual(report.candidate_state_count, 1)
        self.assertEqual(report.oracle_class_count, 2)

    def test_overrefined_key_is_sufficient_but_not_coarsest(self):
        assignments = [("A", "A"), ("A", "B"), ("B", "A"), ("B", "B")]
        report = audit_partition(
            assignments,
            state_key=lambda x: x,  # retains order
            outcome=lambda x: x.count("A"),
        )
        self.assertTrue(report.sufficient)
        self.assertFalse(report.coarsest_for_signature)
        self.assertEqual(report.candidate_state_count, 4)
        self.assertEqual(report.oracle_class_count, 3)
        self.assertEqual(report.excess_states, 1)
        self.assertGreater(len(report.split_pairs), 0)

    def test_oracle_key_attains_coarsest_partition(self):
        assignments = list(itertools.product(("A", "B"), repeat=3))
        outcome = lambda x: x.count("A")
        report = audit_partition(
            assignments,
            state_key=lambda x: outcome_key(x, outcome),
            outcome=outcome,
        )
        self.assertTrue(report.coarsest_for_signature)
        self.assertEqual(report.candidate_state_count, 4)


if __name__ == "__main__":
    unittest.main()
