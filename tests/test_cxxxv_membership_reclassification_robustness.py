import unittest

from cxxxv_membership_reclassification_robustness import (
    Scenario, Stratum, robust_bounds, scenario_bounds,
)


class ReclassificationRobustnessTests(unittest.TestCase):
    def setUp(self):
        # Two admissible classifications of the same 100-person population.
        self.scenarios = [
            Scenario("class-A", (
                Stratum(10, 30, 0.0, 0.2),
                Stratum(20, 30, 0.4, 1.0),
            )),
            Scenario("class-B", (
                Stratum(12, 20, 0.0, 0.2),
                Stratum(18, 40, 0.4, 1.0),
            )),
        ]

    def test_scenario_bounds(self):
        self.assertEqual(scenario_bounds(self.scenarios[0], 100), (0.42, 0.60))
        self.assertAlmostEqual(scenario_bounds(self.scenarios[1], 100)[0], 0.42)
        self.assertAlmostEqual(scenario_bounds(self.scenarios[1], 100)[1], 0.70)

    def test_robust_envelope_uses_extreme_scenarios(self):
        result = robust_bounds(self.scenarios, 100)
        self.assertAlmostEqual(result.lower, 0.42)
        self.assertAlmostEqual(result.upper, 0.70)
        self.assertEqual(result.lower_scenario, "class-A")
        self.assertEqual(result.upper_scenario, "class-B")

    def test_order_independent(self):
        self.assertEqual(robust_bounds(self.scenarios, 100),
                         robust_bounds(reversed(self.scenarios), 100))

    def test_empty_scenarios_rejected(self):
        with self.assertRaises(ValueError):
            robust_bounds([], 100)

    def test_invalid_support_rejected(self):
        bad = Scenario("bad", (Stratum(0, 1, 2, 1),))
        with self.assertRaises(ValueError):
            scenario_bounds(bad, 10)

    def test_missing_count_cannot_exceed_population(self):
        bad = Scenario("bad", (Stratum(0, 11, 0, 1),))
        with self.assertRaises(ValueError):
            scenario_bounds(bad, 10)


if __name__ == "__main__":
    unittest.main()
