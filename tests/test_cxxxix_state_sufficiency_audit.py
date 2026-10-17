import unittest
from cxxxix_state_sufficiency_audit import BoundRule, audit_count_sufficiency


class StateSufficiencyAuditTests(unittest.TestCase):
    def test_count_compression_matches_assignment_space_with_asymmetric_choices(self):
        # Unit 1 can be A/B, unit 2 only B, unit 3 A/B: restrictions differ by unit.
        result = audit_count_sufficiency(
            30, 100, (("A", "B"), ("B",), ("A", "B")),
            {"A": BoundRule(0, .2, 1, 2), "B": BoundRule(.4, 1, 1, 2)})
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["assignment_count"], 3)
        self.assertEqual(result["distinct_count_states"], 2)
        self.assertAlmostEqual(result["lower"], .304)
        self.assertAlmostEqual(result["upper"], .322)

    def test_all_binary_assignments_collapse_to_m_plus_one_states(self):
        m = 12
        result = audit_count_sufficiency(
            10, 100, tuple(("A", "B") for _ in range(m)),
            {"A": BoundRule(0, .2), "B": BoundRule(.4, 1)})
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["assignment_count"], 2 ** m)
        self.assertEqual(result["distinct_count_states"], m + 1)
        self.assertAlmostEqual(result["lower"], .10)
        self.assertAlmostEqual(result["upper"], .22)

    def test_infeasible_constraints_are_rejected(self):
        with self.assertRaises(ValueError):
            audit_count_sufficiency(0, 10, (("A",),), {"A": BoundRule(0, 1, 2, 3)})

    def test_empty_unit_choice_is_rejected(self):
        with self.assertRaises(ValueError):
            audit_count_sufficiency(0, 10, ((),), {"A": BoundRule(0, 1)})


if __name__ == "__main__":
    unittest.main()
