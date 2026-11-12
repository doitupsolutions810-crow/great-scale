import unittest
from robust_value_of_information import robust_measurement_value
BASE = {"prior":[0.5,0.5],"likelihoods":[[1,0],[0,1]],"utilities":[[1,-1],[-1,1]],"cost":0.2}
class RobustValueOfInformationTests(unittest.TestCase):
    def test_positive_in_all_models_recommends_measure(self):
        r=robust_measurement_value([dict(BASE),dict(BASE,cost=0.4)])
        self.assertEqual(r["recommendation"],"MEASURE"); self.assertAlmostEqual(r["worst_case_net_value"],0.6)
    def test_one_unfavorable_model_blocks_robust_recommendation(self):
        r=robust_measurement_value([dict(BASE),dict(BASE,cost=1.1)])
        self.assertEqual(r["recommendation"],"NOT_ROBUSTLY_WORTH_MEASURING"); self.assertAlmostEqual(r["worst_case_net_value"],-0.1)
    def test_reports_range_across_models(self):
        r=robust_measurement_value([dict(BASE,cost=0.2),dict(BASE,cost=0.7)])
        self.assertAlmostEqual(r["net_value_range"][0],0.3); self.assertAlmostEqual(r["net_value_range"][1],0.8)
    def test_empty_model_set_rejected(self):
        with self.assertRaises(ValueError): robust_measurement_value([])
    def test_invalid_model_rejected(self):
        with self.assertRaises(ValueError): robust_measurement_value([{"prior":[1.0]}])
    def test_zero_worst_case_is_not_positive(self):
        r=robust_measurement_value([dict(BASE,cost=1.0)])
        self.assertEqual(r["recommendation"],"NOT_ROBUSTLY_WORTH_MEASURING"); self.assertAlmostEqual(r["worst_case_net_value"],0.0)
if __name__=="__main__": unittest.main()
