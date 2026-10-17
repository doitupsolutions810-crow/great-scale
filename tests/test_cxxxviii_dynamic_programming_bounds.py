import unittest
from cxxxvi_constrained_classification_optimization import (
    MissingUnit as ExactUnit, StratumRule as ExactRule, solve_exact,
)
from cxxxviii_dynamic_programming_bounds import (
    MissingUnit, StratumRule, solve_dp,
)


class DynamicProgrammingBoundsTests(unittest.TestCase):
    def test_matches_exact_enumerator_cxxxvi_case(self):
        units = (MissingUnit(("A", "B")), MissingUnit(("A", "B")), MissingUnit(("B",)))
        rules = {"A": StratumRule(0, 0.2, 1, 2), "B": StratumRule(0.4, 1, 1, 2)}
        dp = solve_dp(30, 100, units, rules)
        exact = solve_exact(30, 100,
            tuple(ExactUnit(u.allowed_strata) for u in units),
            {k: ExactRule(v.lower, v.upper, v.min_missing, v.max_missing) for k, v in rules.items()})
        self.assertAlmostEqual(dp.lower, exact.lower)
        self.assertAlmostEqual(dp.upper, exact.upper)
        self.assertEqual(dp.feasible_count_vectors, 2)

    def test_many_equivalent_assignments_collapse_to_count_states(self):
        units = tuple(MissingUnit(("A", "B")) for _ in range(12))
        rules = {"A": StratumRule(0, 0.2, 0, 12), "B": StratumRule(0.4, 1, 0, 12)}
        dp = solve_dp(10, 100, units, rules)
        self.assertEqual(dp.feasible_count_vectors, 13)
        self.assertLess(dp.processed_states, 100)
        self.assertAlmostEqual(dp.lower, 0.10)
        self.assertAlmostEqual(dp.upper, 0.22)

    def test_no_feasible_assignment(self):
        units = (MissingUnit(("A",)),)
        rules = {"A": StratumRule(0, 1, 2, 3)}
        with self.assertRaises(ValueError):
            solve_dp(0, 10, units, rules)

    def test_invalid_support(self):
        with self.assertRaises(ValueError):
            solve_dp(0, 10, (), {"A": StratumRule(2, 1)})


if __name__ == "__main__":
    unittest.main()
