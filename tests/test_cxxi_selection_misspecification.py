import unittest
from cxxi_selection_misspecification import run_misspecification_test

class SelectionMisspecificationTests(unittest.TestCase):
    def test_known_truth_and_methods(self):
        r=run_misspecification_test(simulations=200,seed=17,logit_shift=0.0)
        self.assertTrue(r["synthetic_only"])
        self.assertAlmostEqual(r["true_equal_cluster_mean"],0.125)
        self.assertEqual(set(r["results"]),{
            "observed_equal_cluster","ipw_true_probability","ipw_misspecified"})
        self.assertEqual(r["results"]["ipw_true_probability"],
                         r["results"]["ipw_misspecified"])

    def test_misspecification_is_deterministic_and_bounded(self):
        a=run_misspecification_test(simulations=200,seed=22,logit_shift=1.0)
        b=run_misspecification_test(simulations=200,seed=22,logit_shift=1.0)
        self.assertEqual(a,b)
        self.assertGreater(a["mean_misspecified_weight_ess"],0)
        self.assertLessEqual(a["mean_misspecified_weight_ess"],200)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            run_misspecification_test(simulations=20)
        with self.assertRaises(ValueError):
            run_misspecification_test(logit_shift=float("inf"))

if __name__ == "__main__":
    unittest.main()
