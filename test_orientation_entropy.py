#!/usr/bin/env python3
"""Analytic identifiability checks for Great Scale Descent XCI."""
import math
import unittest

def heat_from_eta(eta):
    return (1.0 - eta * eta) / 4.0

def entropy_from_eta(eta):
    p = (1.0 + eta) / 2.0
    q = (1.0 - eta) / 2.0
    return sum(-x * math.log(x) for x in (p, q) if x > 0.0)

def probabilities_from_heat(s):
    d = math.sqrt(max(0.0, 1.0 - 4.0 * s))
    return ((1.0 - d) / 2.0, (1.0 + d) / 2.0)

class IdentifiabilityTests(unittest.TestCase):
    def test_entropy_blind_to_orientation_sign(self):
        for eta in (-1.0, -0.7, -0.2, 0.0, 0.2, 0.7, 1.0):
            self.assertAlmostEqual(heat_from_eta(eta), heat_from_eta(-eta), places=14)
            self.assertAlmostEqual(entropy_from_eta(eta), entropy_from_eta(-eta), places=14)

    def test_heat_recovers_unordered_probabilities(self):
        for eta in (-0.9, -0.5, 0.0, 0.5, 0.9):
            s = heat_from_eta(eta)
            actual = sorted(((1 + eta) / 2, (1 - eta) / 2))
            recovered = sorted(probabilities_from_heat(s))
            for a, b in zip(actual, recovered):
                self.assertAlmostEqual(a, b, places=14)

    def test_zero_chern_erases_area(self):
        for area in (0.01, 0.5, 1.0, 3.7, 100.0):
            eta = 0.0 / area
            self.assertEqual(heat_from_eta(eta), 0.25)
            self.assertAlmostEqual(entropy_from_eta(eta), math.log(2), places=14)

    def test_nonzero_chern_area_reconstruction(self):
        for c, area in ((1, 1.7), (-1, 1.7), (2, 4.2), (-3, 5.1)):
            eta = c / area
            s = heat_from_eta(eta)
            recovered = abs(c) / math.sqrt(1 - 4 * s)
            self.assertAlmostEqual(recovered, area, places=12)

    def test_entropy_is_derived_not_independent(self):
        for eta in (-0.99, -0.4, 0.0, 0.4, 0.99):
            s = heat_from_eta(eta)
            p0, p1 = probabilities_from_heat(s)
            h_from_s = -sum(p * math.log(p) for p in (p0, p1) if p > 0)
            self.assertAlmostEqual(h_from_s, entropy_from_eta(eta), places=14)

if __name__ == "__main__":
    unittest.main(verbosity=2)
