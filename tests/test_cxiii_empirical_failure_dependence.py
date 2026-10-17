import unittest
from cxiii_empirical_failure_dependence import analyze_failure_trials, analyze_domains

class EmpiricalFailureDependenceTests(unittest.TestCase):
    def test_perfect_cofailure_has_positive_excess(self):
        trials=[{"failures":{"a":True,"b":True}},{"failures":{"a":False,"b":False}}]*5
        r=analyze_failure_trials(trials,"a","b")
        self.assertAlmostEqual(r["joint_failure_rate"],0.5)
        self.assertAlmostEqual(r["independence_benchmark"],0.25)
        self.assertAlmostEqual(r["excess_joint_failure"],0.25)
        self.assertAlmostEqual(r["phi_correlation"],1.0)
    def test_independent_balanced_pattern_zero_excess(self):
        trials=[{"failures":{"a":a,"b":b}} for a,b in [(True,True),(True,False),(False,True),(False,False)]*3]
        r=analyze_failure_trials(trials,"a","b")
        self.assertAlmostEqual(r["excess_joint_failure"],0.0)
        self.assertAlmostEqual(r["phi_correlation"],0.0)
    def test_constant_outcome_correlation_undefined(self):
        trials=[{"failures":{"a":False,"b":x}} for x in [True,False,True]]
        self.assertIsNone(analyze_failure_trials(trials,"a","b")["phi_correlation"])
    def test_missing_observer_rejected(self):
        with self.assertRaises(ValueError): analyze_failure_trials([{"failures":{"a":True}}],"a","b")
    def test_non_boolean_rejected(self):
        with self.assertRaises(ValueError): analyze_failure_trials([{"failures":{"a":1,"b":False}}],"a","b")
    def test_empty_trials_rejected(self):
        with self.assertRaises(ValueError): analyze_failure_trials([],"a","b")
    def test_same_observer_rejected(self):
        with self.assertRaises(ValueError): analyze_failure_trials([{"failures":{"a":False}}],"a","a")
    def test_domain_comparison_reports_pairs(self):
        trials=[{"failures":{"a":True,"b":True,"c":False}},
                {"failures":{"a":False,"b":False,"c":True}},
                {"failures":{"a":True,"b":True,"c":False}},
                {"failures":{"a":False,"b":False,"c":True}}]
        r=analyze_domains(trials,{"a":"x","b":"x","c":"y"})
        self.assertEqual(len(r["pair_diagnostics"]),3)
        self.assertIsNotNone(r["mean_excess_same_domain"])
        self.assertIsNotNone(r["mean_excess_different_domain"])

if __name__ == "__main__": unittest.main()
