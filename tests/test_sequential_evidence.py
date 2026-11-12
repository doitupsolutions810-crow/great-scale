import math
import unittest

from sequential_evidence import (
    bonferroni_alpha,
    sequential_disposition,
    sprt_wald_boundaries,
    ville_threshold,
)


class SequentialEvidenceTests(unittest.TestCase):
    def test_bonferroni_allocation(self):
        self.assertAlmostEqual(bonferroni_alpha(0.05, 10), 0.005)

    def test_ville_threshold(self):
        self.assertAlmostEqual(ville_threshold(0.05), 20.0)

    def test_crossing_and_non_crossing(self):
        self.assertEqual(sequential_disposition(20.0, 0.05), "CROSSING_THRESHOLD_ELIGIBLE_FOR_REVIEW")
        self.assertEqual(sequential_disposition(19.99, 0.05), "CONTINUE_OR_INCONCLUSIVE")

    def test_not_crossing_does_not_accept_null(self):
        self.assertEqual(sequential_disposition(0.2, 0.05), "CONTINUE_OR_INCONCLUSIVE")

    def test_sprt_wald_boundaries(self):
        a, b = sprt_wald_boundaries(0.05, 0.10)
        self.assertAlmostEqual(a, 18.0)
        self.assertAlmostEqual(b, 0.10 / 0.95)

    def test_invalid_inputs(self):
        for alpha in (0, 1, -0.1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                ville_threshold(alpha)
        with self.assertRaises(ValueError):
            bonferroni_alpha(0.05, 0)
        with self.assertRaises(ValueError):
            sequential_disposition(-1, 0.05)
