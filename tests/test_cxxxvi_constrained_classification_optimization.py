import unittest
from itertools import product

from cxxxvi_constrained_classification_optimization import (
    MissingUnit, StratumRule, solve_exact,
)


class ConstrainedClassificationTests(unittest.TestCase):
    def setUp(self):
        self.units = (
            MissingUnit(("A", "B")),
            MissingUnit(("A", "B")),
            MissingUnit(("B",)),
        )
        self.rules = {
            "A": StratumRule(0.0, 0.2, min_missing=1, max_missing=2),
            "B": StratumRule(0.4, 1.0, min_missing=1, max_missing=2),
        }

    def test_exact_small_case(self):
        result = solve_exact(30.0, 100, self.units, self.rules)
        self.assertAlmostEqual(result.lower, 0.304)
        self.assertAlmostEqual(result.upper, 0.322)
        self.assertEqual(result.feasible_assignments, 3)

    def test_matches_independent_exhaustive_oracle(self):
        result = solve_exact(30.0, 100, self.units, self.rules)
        feasible = []
        for assignment in product(("A", "B"), ("A", "B"), ("B",)):
            counts = {k: assignment.count(k) for k in self.rules}
            if all(self.rules[k].min_missing <= counts[k] <= self.rules[k].max_missing for k in self.rules):
                lower = (30.0 + sum(counts[k] * self.rules[k].lower for k in self.rules)) / 100
                upper = (30.0 + sum(counts[k] * self.rules[k].upper for k in self.rules)) / 100
                feasible.append((lower, upper))
        self.assertEqual(result.lower, min(x[0] for x in feasible))
        self.assertEqual(result.upper, max(x[1] for x in feasible))

    def test_infeasible_constraints_rejected(self):
        rules = {
            "A": StratumRule(0.0, 0.2, min_missing=3),
            "B": StratumRule(0.4, 1.0, min_missing=2),
        }
        with self.assertRaises(ValueError):
            solve_exact(30.0, 100, self.units, rules)

    def test_unknown_stratum_not_allowed(self):
        with self.assertRaises(ValueError):
            solve_exact(30.0, 100, (MissingUnit(("Z",)),), self.rules)

    def test_invalid_support_rejected(self):
        with self.assertRaises(ValueError):
            solve_exact(0.0, 10, (), {"A": StratumRule(1.0, 0.0)})


if __name__ == "__main__":
    unittest.main()
