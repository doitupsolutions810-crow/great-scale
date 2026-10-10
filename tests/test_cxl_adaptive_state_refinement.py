import unittest
from cxl_adaptive_state_refinement import audit_unit_specific_contributions


class AdaptiveStateRefinementTests(unittest.TestCase):
    def test_same_counts_can_have_different_objectives(self):
        result = audit_unit_specific_contributions(
            allowed=(("A", "B"), ("A", "B")),
            contributions=(
                {"A": (0.0, 0.1), "B": (0.4, 0.5)},
                {"A": (0.2, 0.3), "B": (0.6, 0.7)},
            ),
            population=10,
        )
        self.assertEqual(result["assignment_count"], 4)
        self.assertEqual(result["count_state_count"], 3)
        self.assertFalse(result["count_only_sufficient"])
        # Mixed assignments AB and BA have the same counts, but different sums.
        ab = next(x for x in result["assignments"] if x["assignment"] == ["A", "B"])
        ba = next(x for x in result["assignments"] if x["assignment"] == ["B", "A"])
        self.assertEqual(ab["counts"], ba["counts"])
        self.assertNotEqual(ab["lower_sum"], ba["lower_sum"])
        self.assertEqual(result["refined_state_count"], 4)

    def test_homogeneous_contributions_make_count_state_sufficient(self):
        result = audit_unit_specific_contributions(
            allowed=(("A", "B"),) * 3,
            contributions=({"A": (0.0, 0.2), "B": (0.4, 1.0)},) * 3,
            population=10,
        )
        self.assertTrue(result["count_only_sufficient"])
        self.assertEqual(result["assignment_count"], 8)
        self.assertEqual(result["count_state_count"], 4)

    def test_rejects_missing_contribution(self):
        with self.assertRaises(ValueError):
            audit_unit_specific_contributions((("A",),), ({},), 10)


if __name__ == "__main__":
    unittest.main()
