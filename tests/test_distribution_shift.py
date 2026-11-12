import math
import unittest

from distribution_shift import (
    bounded_risk_transfer_bound,
    risk_shift_budget,
    transfer_status,
)


class DistributionShiftTests(unittest.TestCase):
    def test_transfer_bound(self):
        self.assertAlmostEqual(bounded_risk_transfer_bound(0.05, 1.0, 0.10), 0.15)

    def test_bound_clips_at_loss_maximum(self):
        self.assertEqual(bounded_risk_transfer_bound(0.9, 1.0, 0.5), 1.0)

    def test_transfer_status(self):
        self.assertEqual(transfer_status(0.05, 1.0, 0.10, 0.15), "BOUND_WITHIN_LIMIT")
        self.assertEqual(transfer_status(0.05, 1.0, 0.20, 0.15), "TRANSFER_NOT_CERTIFIED")

    def test_risk_shift_budget(self):
        self.assertAlmostEqual(risk_shift_budget(0.05, 1.0, 0.15), 0.10)

    def test_no_budget_when_historical_risk_too_high(self):
        self.assertEqual(risk_shift_budget(0.2, 1.0, 0.1), 0.0)

    def test_invalid_inputs(self):
        for bad in (-0.1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                bounded_risk_transfer_bound(bad, 1.0, 0.1)
        with self.assertRaises(ValueError):
            bounded_risk_transfer_bound(0.1, 1.0, 1.1)
