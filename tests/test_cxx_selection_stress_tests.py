import unittest
from cxx_selection_stress_tests import build_population, run_selection_stress_test

class TestCXX(unittest.TestCase):
    def test_population_has_known_truth(self):
        pop=build_population(40)
        self.assertEqual(len(pop),40)
        self.assertAlmostEqual(sum(c["delta"] for c in pop)/40,0.125)

    def test_reproducible_and_returns_metrics(self):
        a=run_selection_stress_test(n_clusters=40,simulations=100,bootstrap_reps=100,seed=8,mechanism="effect_correlated")
        b=run_selection_stress_test(n_clusters=40,simulations=100,bootstrap_reps=100,seed=8,mechanism="effect_correlated")
        self.assertEqual(a,b)
        for method in ("observed_equal_cluster","ipw_hajek"):
            self.assertIn("bias",a["results"][method])
            self.assertIn("interval_coverage",a["results"][method])

    def test_size_correlated_mechanism(self):
        r=run_selection_stress_test(n_clusters=40,simulations=100,bootstrap_reps=100,seed=9,mechanism="size_correlated")
        self.assertEqual(r["mechanism"],"size_correlated")
        self.assertAlmostEqual(r["true_equal_cluster_mean"],0.125)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            build_population(5)
        with self.assertRaises(ValueError):
            run_selection_stress_test(simulations=10)
        with self.assertRaises(ValueError):
            run_selection_stress_test(mechanism="unknown")

if __name__ == "__main__":
    unittest.main()
