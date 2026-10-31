import unittest
from cxxii_partial_identification_selection import selection_bounds, run_partial_identification_test

class PartialIdentificationTests(unittest.TestCase):
    def test_bounds_contain_equal_weight_mean(self):
        values=[0.0,0.0,0.25,0.25]
        b=selection_bounds(values,pi_min=0.2,pi_max=0.8)
        self.assertLessEqual(b["lower"],sum(values)/len(values))
        self.assertGreaterEqual(b["upper"],sum(values)/len(values))
        self.assertLessEqual(b["lower"],b["upper"])

    def test_equal_probability_range_collapses(self):
        b=selection_bounds([0.0,0.25,0.25],pi_min=0.5,pi_max=0.5)
        self.assertAlmostEqual(b["lower"],b["upper"])
        self.assertAlmostEqual(b["lower"],1/6)

    def test_invalid_inputs(self):
        for args in [([],{}),([-0.1],{}),([float("nan")],{}),([0.0],{"pi_min":0})]:
            with self.assertRaises(ValueError):
                selection_bounds(args[0],**args[1])

    def test_demo_is_deterministic(self):
        a=run_partial_identification_test(seed=41)
        b=run_partial_identification_test(seed=41)
        self.assertEqual(a,b)

if __name__ == "__main__":
    unittest.main()
