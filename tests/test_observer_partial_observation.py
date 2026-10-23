import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from observer_checkpoint_consistency import checkpoint_body, sign_checkpoint
from observer_partial_observation import compare_partial_observer_views


class PartialObservationTests(unittest.TestCase):
    def setUp(self):
        self.keys = {name: Ed25519PrivateKey.generate() for name in ("a", "b", "c")}
        self.trusted = {name: key.public_key() for name, key in self.keys.items()}

    def cp(self, signer, size, head, parent="0" * 64):
        return sign_checkpoint(checkpoint_body("registry-log", size, head, parent), signer, self.keys[signer])

    def test_complete_consistent_pair_coverage(self):
        a = self.cp("a", 1, "a" * 64); b = self.cp("b", 1, "a" * 64); c = self.cp("c", 1, "a" * 64)
        result = compare_partial_observer_views([a, b, c], self.trusted, [(0, 1), (0, 2), (1, 2)])
        self.assertEqual(result["classification"], "CONSISTENT")
        self.assertTrue(result["consistency_established_for_supplied_set"])

    def test_missing_pair_is_partial_not_consistent(self):
        a = self.cp("a", 1, "a" * 64); b = self.cp("b", 1, "a" * 64); c = self.cp("c", 1, "a" * 64)
        result = compare_partial_observer_views([a, b, c], self.trusted, [(0, 1)])
        self.assertEqual(result["classification"], "PARTIAL_EVIDENCE")
        self.assertEqual(len(result["missing_pairs"]), 2)

    def test_observed_fork_dominates_missing_edges(self):
        a = self.cp("a", 2, "a" * 64); b = self.cp("b", 2, "b" * 64); c = self.cp("c", 1, "c" * 64)
        result = compare_partial_observer_views([a, b, c], self.trusted, [(0, 1)])
        self.assertEqual(result["classification"], "FORK")
        self.assertEqual(len(result["missing_pairs"]), 2)

    def test_complete_but_incomparable_is_not_consistent(self):
        a = self.cp("a", 1, "a" * 64); b = self.cp("b", 2, "b" * 64); c = self.cp("c", 3, "c" * 64)
        result = compare_partial_observer_views([a, b, c], self.trusted, [(0, 1), (0, 2), (1, 2)])
        self.assertEqual(result["classification"], "INCOMPARABLE")

    def test_same_state_different_lineage_blocks_consistent(self):
        a = self.cp("a", 2, "b" * 64, "1" * 64); b = self.cp("b", 2, "b" * 64, "2" * 64)
        result = compare_partial_observer_views([a, b], self.trusted, [(0, 1)])
        self.assertEqual(result["classification"], "INCOMPARABLE")
        self.assertFalse(result["consistency_established_for_supplied_set"])

    def test_duplicate_pair_rejected(self):
        a = self.cp("a", 1, "a" * 64); b = self.cp("b", 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "duplicate observed pair"):
            compare_partial_observer_views([a, b], self.trusted, [(0, 1), (1, 0)])

    def test_bad_index_rejected(self):
        a = self.cp("a", 1, "a" * 64); b = self.cp("b", 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "valid"):
            compare_partial_observer_views([a, b], self.trusted, [(0, 2)])

    def test_duplicate_signer_rejected(self):
        a = self.cp("a", 1, "a" * 64); b = self.cp("a", 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "distinct signer"):
            compare_partial_observer_views([a, b], self.trusted, [(0, 1)])

    def test_forged_checkpoint_rejected(self):
        a = self.cp("a", 1, "a" * 64); b = self.cp("b", 1, "b" * 64)
        b["body"]["head_hash"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "valid signatures"):
            compare_partial_observer_views([a, b], self.trusted, [(0, 1)])


if __name__ == "__main__":
    unittest.main()
