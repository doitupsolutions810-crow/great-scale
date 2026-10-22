import unittest
from great_scale.calibration_validity import assess_calibration, CalibrationState, CalibrationMonitor

class CalibrationTests(unittest.TestCase):
    def test_valid_interval(self):
        self.assertEqual(assess_calibration(.5,.1,1).state, CalibrationState.VALID)
    def test_invalid_interval(self):
        self.assertEqual(assess_calibration(1.5,.1,1).state, CalibrationState.INVALID)
    def test_overlap_is_degraded(self):
        self.assertEqual(assess_calibration(.95,.1,1).state, CalibrationState.DEGRADED)
    def test_negative_residual_uses_magnitude(self):
        self.assertEqual(assess_calibration(-1.5,.1,1).state, CalibrationState.INVALID)
    def test_rejects_bad_inputs(self):
        for args in ((0,-1,1),(0,0,0),(float('nan'),0,1)):
            with self.assertRaises(ValueError): assess_calibration(*args)
    def test_requires_consecutive_clean_checks_to_recover(self):
        m=CalibrationMonitor(1,recovery_checks=3)
        self.assertEqual(m.update(1.5,.1),CalibrationState.INVALID)
        self.assertEqual(m.update(.2,.1),CalibrationState.INVALID)
        self.assertEqual(m.update(.2,.1),CalibrationState.INVALID)
        self.assertEqual(m.update(.2,.1),CalibrationState.VALID)
    def test_uncertain_check_resets_recovery_streak(self):
        m=CalibrationMonitor(1,recovery_checks=2)
        m.update(1.5,.1); m.update(.2,.1); m.update(.95,.1)
        self.assertEqual(m.update(.2,.1),CalibrationState.INVALID)
        self.assertEqual(m.update(.2,.1),CalibrationState.VALID)
    def test_recalibration_requires_new_checks(self):
        m=CalibrationMonitor(1,recovery_checks=1); m.update(.2,.1)
        self.assertEqual(m.state,CalibrationState.VALID)
        self.assertEqual(m.recalibrate(),2)
        self.assertEqual(m.state,CalibrationState.DEGRADED)

if __name__ == "__main__": unittest.main()
