import unittest

from cxliii_optimization_equivalence import audit_optimization_compression


class OptimizationEquivalenceTests(unittest.TestCase):
    def test_outcome_key_preserves_feasibility_objective_and_optimum(self):
        items = ["a0", "a1", "b0", "b1"]
        outcome = {"a0": ("A", True, 2), "a1": ("A", True, 2),
                   "b0": ("B", True, 5), "b1": ("B", True, 5)}
        report = audit_optimization_compression(
            items, lambda x: outcome[x][0],
            lambda x: outcome[x][1], lambda x: outcome[x][2])
        self.assertTrue(report.feasible_set_preserved)
        self.assertTrue(report.objective_preserved)
        self.assertTrue(report.optimum_preserved)
        self.assertEqual(report.original_optimum, 2)

    def test_feasibility_collision_is_detected_even_if_optimum_matches(self):
        items = ["good", "bad"]
        data = {"good": ("same", True, 1), "bad": ("same", False, 9)}
        report = audit_optimization_compression(
            items, lambda x: data[x][0],
            lambda x: data[x][1], lambda x: data[x][2])
        self.assertFalse(report.feasible_set_preserved)
        self.assertFalse(report.optimum_preserved is False)  # optimum may coincide by chance
        self.assertEqual(len(report.collision_witnesses), 1)

    def test_objective_collision_detected(self):
        items = ["x", "y"]
        data = {"x": ("same", True, 1), "y": ("same", True, 3)}
        report = audit_optimization_compression(
            items, lambda x: data[x][0],
            lambda x: data[x][1], lambda x: data[x][2])
        self.assertFalse(report.objective_preserved)
        self.assertEqual(len(report.collision_witnesses), 1)

    def test_overrefined_key_preserves_optimum_but_more_states(self):
        items = ["x1", "x2", "y"]
        data = {"x1": (True, 1), "x2": (True, 1), "y": (True, 4)}
        report = audit_optimization_compression(
            items, lambda x: x, lambda x: data[x][0], lambda x: data[x][1])
        self.assertTrue(report.feasible_set_preserved)
        self.assertTrue(report.objective_preserved)
        self.assertTrue(report.optimum_preserved)
        self.assertEqual(report.compressed_state_count, 3)


if __name__ == "__main__":
    unittest.main()
