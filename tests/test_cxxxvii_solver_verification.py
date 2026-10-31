import unittest
from itertools import product

from cxxxvi_constrained_classification_optimization import (
    MissingUnit, StratumRule, solve_exact,
)
from cxxxvii_solver_verification import exhaustive_oracle, assert_matches


class SolverVerificationTests(unittest.TestCase):
    def test_cxxxvi_case_against_independent_oracle(self):
        units = (MissingUnit(("A", "B")), MissingUnit(("A", "B")), MissingUnit(("B",)))
        rules = {
            "A": StratumRule(0.0, 0.2, 1, 2),
            "B": StratumRule(0.4, 1.0, 1, 2),
        }
        candidate = solve_exact(30.0, 100, units, rules)
        oracle = exhaustive_oracle(30.0, 100,
            (("A", "B"), ("A", "B"), ("B",)),
            {"A": {"lower": 0.0, "upper": 0.2, "min_missing": 1, "max_missing": 2},
             "B": {"lower": 0.4, "upper": 1.0, "min_missing": 1, "max_missing": 2}})
        self.assertTrue(assert_matches(candidate, oracle))
        self.assertEqual(oracle["feasible_assignments"], 3)
        self.assertAlmostEqual(oracle["lower"], 0.304)
        self.assertAlmostEqual(oracle["upper"], 0.322)

    def test_relaxing_constraints_cannot_shrink_outer_bounds(self):
        units = (MissingUnit(("A", "B")), MissingUnit(("A", "B")), MissingUnit(("B",)))
        tight = {"A": StratumRule(0.0, 0.2, 1, 2), "B": StratumRule(0.4, 1.0, 1, 2)}
        relaxed = {"A": StratumRule(0.0, 0.2, 0, 3), "B": StratumRule(0.4, 1.0, 0, 3)}
        a = solve_exact(30.0, 100, units, tight)
        b = solve_exact(30.0, 100, units, relaxed)
        self.assertLessEqual(b.lower, a.lower)
        self.assertGreaterEqual(b.upper, a.upper)

    def test_small_allowed_assignment_space_count(self):
        # All eight binary assignments of three units are feasible when no count
        # constraints are active; the oracle should enumerate exactly eight.
        units = (("A", "B"), ("A", "B"), ("A", "B"))
        strata = {
            "A": {"lower": 0.0, "upper": 0.2, "min_missing": 0, "max_missing": 3},
            "B": {"lower": 0.4, "upper": 1.0, "min_missing": 0, "max_missing": 3},
        }
        result = exhaustive_oracle(10.0, 20, units, strata)
        self.assertEqual(result["feasible_assignments"], 8)
        self.assertAlmostEqual(result["lower"], 0.11)
        self.assertAlmostEqual(result["upper"], 0.65)


if __name__ == "__main__":
    unittest.main()
