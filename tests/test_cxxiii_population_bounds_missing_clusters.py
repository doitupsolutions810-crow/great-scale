import itertools
import unittest
from cxxiii_population_bounds_missing_clusters import population_mean_bounds, run_population_bounds_test

class PopulationBoundsTests(unittest.TestCase):
    def test_contains_all_completions_small_frame(self):
        observed=[0.0,0.25]
        b=population_mean_bounds(observed,population_size=4,outcome_min=0.0,outcome_max=0.25)
        completions=[(sum(observed)+x+y)/4
                     for x,y in itertools.product([0.0,0.25],repeat=2)]
        self.assertAlmostEqual(b["lower"],min(completions))
        self.assertAlmostEqual(b["upper"],max(completions))
        self.assertTrue(all(b["lower"] <= x <= b["upper"] for x in completions))

    def test_complete_frame_collapses(self):
        b=population_mean_bounds([0.0,0.25,0.0],population_size=3,
                                 outcome_min=0.0,outcome_max=0.25)
        self.assertAlmostEqual(b["lower"],b["upper"])
        self.assertAlmostEqual(b["lower"],1/12)

    def test_repeated_synthetic_target_is_contained(self):
        for seed in range(25):
            r=run_population_bounds_test(seed=seed)
            self.assertTrue(r["target_inside_bounds"],msg=f"seed={seed}")

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            population_mean_bounds([0.1],population_size=0,outcome_min=0,outcome_max=1)
        with self.assertRaises(ValueError):
            population_mean_bounds([0.3],population_size=1,outcome_min=0,outcome_max=0.25)
        with self.assertRaises(ValueError):
            population_mean_bounds([0.1,0.2],population_size=1,outcome_min=0,outcome_max=1)

if __name__ == "__main__":
    unittest.main()
