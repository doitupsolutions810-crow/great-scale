import math
import unittest

from loss_envelope import (
    NEGATIVE_LOG,
    POWER_BARRIER,
    fixed_moment_envelope,
    loss_derivative,
    loss_third_derivative,
    loss_value,
    robust_chord_bound,
)


class LossEnvelopeTests(unittest.TestCase):
    def test_third_derivative_is_positive_on_supported_interval(self):
        for loss, power in ((NEGATIVE_LOG, 1.0), (POWER_BARRIER, 0.75), (POWER_BARRIER, 3.0)):
            for x in (0.0, 0.2, 0.6, 0.95):
                self.assertGreater(
                    loss_third_derivative(loss, x, scale=1.7, power=power),
                    0.0,
                )

    def test_fixed_moment_witness_reconstructs_mean_and_variance(self):
        for loss, power in ((NEGATIVE_LOG, 1.0), (POWER_BARRIER, 1.4)):
            result = fixed_moment_envelope(
                0.50, 0.05, 0.05, loss=loss, scale=1.0, power=power
            )
            self.assertEqual(result["method"], "SHARP_FIXED_MOMENT")
            self.assertEqual(result["status"], "PROVED_FIXED_MOMENT")
            self.assertGreater(result["third_derivative_lower_bound"], 0.0)
            witness = result["witness"]
            probs = [entry["probability"] for entry in witness]
            points = [entry["point"] for entry in witness]
            self.assertAlmostEqual(sum(probs), 1.0, places=12)
            mean = sum(w * x for w, x in zip(probs, points))
            variance = sum(w * (x - result["mean"]) ** 2 for w, x in zip(probs, points))
            expected = sum(
                w * loss_value(loss, x, scale=1.0, power=power)
                for w, x in zip(probs, points)
            )
            self.assertAlmostEqual(mean, result["mean"], places=12)
            self.assertAlmostEqual(variance, result["variance"], places=12)
            self.assertAlmostEqual(expected, result["bound"], places=12)

    def test_negative_log_illustrative_value_is_reproducible(self):
        result = fixed_moment_envelope(0.50, 0.05, 0.05, loss=NEGATIVE_LOG)
        self.assertAlmostEqual(result["bound"], 0.9881707006336746, places=12)
        self.assertAlmostEqual(result["witness"][1]["probability"], 0.19801980198019808, places=12)

    def test_hermite_quadratic_majorizes_each_supported_loss(self):
        b = 0.95
        for loss, power in ((NEGATIVE_LOG, 1.0), (POWER_BARRIER, 1.3)):
            envelope = fixed_moment_envelope(
                0.50, 0.05, 0.05, loss=loss, power=power
            )
            c = envelope["witness"][0]["point"]
            f_c = loss_value(loss, c, power=power)
            f_b = loss_value(loss, b, power=power)
            fp_c = loss_derivative(loss, c, power=power)
            quadratic = (
                f_b - f_c - fp_c * (b - c)
            ) / ((b - c) ** 2)
            for index in range(101):
                x = b * index / 100.0
                q_x = f_c + fp_c * (x - c) + quadratic * (x - c) ** 2
                f_x = loss_value(loss, x, power=power)
                self.assertLessEqual(f_x, q_x + 2e-10, msg=f"{loss=} {x=}")

    def test_chord_fallback_dominates_a_discrete_distribution(self):
        support = [0.1, 0.4, 0.9]
        weights = [0.2, 0.3, 0.5]
        mean = sum(w * x for w, x in zip(weights, support))
        variance = sum(w * (x - mean) ** 2 for w, x in zip(weights, support))
        for loss, power in ((NEGATIVE_LOG, 1.0), (POWER_BARRIER, 2.0)):
            actual = sum(
                w * loss_value(loss, x, power=power)
                for w, x in zip(weights, support)
            )
            result = robust_chord_bound(
                mean, mean, variance, variance, 0.05,
                loss=loss, power=power,
            )
            self.assertEqual(result["method"], "CHORD_FALLBACK")
            self.assertEqual(result["status"], "CERTIFIED_ANALYTIC_BOUND")
            self.assertEqual(result["robust_global_status"], "NOT_CERTIFIED")
            self.assertGreaterEqual(result["bound"] + 1e-12, actual)
            self.assertGreaterEqual(result["feasible_mean_interval"][0], 0.0)
            self.assertLessEqual(result["feasible_mean_interval"][1], 0.95)

    def test_chord_rejects_an_empty_uncertain_moment_set(self):
        with self.assertRaisesRegex(ValueError, "empty feasible moment set"):
            robust_chord_bound(0.80, 0.90, 0.20, 0.25, 0.05)

    def test_fixed_moment_envelope_rejects_invalid_moments(self):
        with self.assertRaisesRegex(ValueError, "variance must be nonnegative"):
            fixed_moment_envelope(0.5, -0.01, 0.05)
        with self.assertRaisesRegex(ValueError, "variance exceeds"):
            fixed_moment_envelope(0.5, 0.30, 0.05)
        with self.assertRaisesRegex(ValueError, "mean must lie"):
            fixed_moment_envelope(0.97, 0.0, 0.05)
        with self.assertRaisesRegex(ValueError, "epsilon_lower"):
            fixed_moment_envelope(0.5, 0.01, 0.0)

    def test_loss_family_parameters_and_domain_are_checked(self):
        with self.assertRaisesRegex(ValueError, "unsupported loss family"):
            loss_value("arbitrary_convex", 0.4)
        with self.assertRaisesRegex(ValueError, "exponent must be finite and positive"):
            loss_value(POWER_BARRIER, 0.4, power=0.0)
        with self.assertRaisesRegex(ValueError, "in \[0, 1\)"):
            loss_value(NEGATIVE_LOG, 1.0)

    def test_zero_width_support_has_zero_risk_when_feasible(self):
        result = robust_chord_bound(0.0, 0.0, 0.0, 0.0, 1.0)
        self.assertEqual(result["bound"], 0.0)
        self.assertEqual(result["support"], [0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
