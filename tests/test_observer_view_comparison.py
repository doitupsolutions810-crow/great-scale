import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from observer_checkpoint_consistency import checkpoint_body, sign_checkpoint, checkpoint_id
from observer_view_comparison import compare_observer_views


class ObserverViewComparisonTests(unittest.TestCase):
    def setUp(self):
        self.keys = {name: Ed25519PrivateKey.generate() for name in ("a", "b", "c")}
        self.trusted = {name: key.public_key() for name, key in self.keys.items()}
        self.domains = {"a": "cloud-1", "b": "cloud-2", "c": "cloud-3"}

    def cp(self, signer, size, head, parent="0" * 64, log="registry-log"):
        body = checkpoint_body(log, size, head, parent)
        return sign_checkpoint(body, signer, self.keys[signer])

    def test_two_distinct_observers_same_view(self):
        a = self.cp("a", 1, "a" * 64)
        b = self.cp("b", 1, "a" * 64)
        result = compare_observer_views([a, b], self.trusted)
        self.assertEqual(result["classification"], "CONSISTENT")
        self.assertEqual(result["distinct_signer_count"], 2)
        self.assertIsNone(result["distinct_fault_domain_count"])

    def test_conflicting_views_detected(self):
        a = self.cp("a", 4, "a" * 64)
        b = self.cp("b", 4, "b" * 64)
        result = compare_observer_views([a, b], self.trusted)
        self.assertEqual(result["classification"], "FORK")
        self.assertEqual(result["pairwise_results"][0]["relation"], "FORK")

    def test_directly_linked_views_consistent(self):
        a = self.cp("a", 1, "a" * 64)
        b = self.cp("b", 2, "b" * 64, checkpoint_id(a))
        result = compare_observer_views([a, b], self.trusted)
        self.assertEqual(result["classification"], "CONSISTENT")

    def test_unlinked_views_incomparable(self):
        a = self.cp("a", 1, "a" * 64)
        b = self.cp("b", 2, "b" * 64)
        result = compare_observer_views([a, b], self.trusted)
        self.assertEqual(result["classification"], "INCOMPARABLE")

    def test_same_state_different_lineage_blocks_consistent(self):
        a = self.cp("a", 2, "b" * 64, "1" * 64)
        b = self.cp("b", 2, "b" * 64, "2" * 64)
        result = compare_observer_views([a, b], self.trusted)
        self.assertEqual(result["classification"], "INCOMPARABLE")
        self.assertEqual(result["pairwise_results"][0]["relation"], "INCOMPARABLE")

    def test_duplicate_signer_cannot_fake_quorum(self):
        a = self.cp("a", 1, "a" * 64)
        b = self.cp("a", 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "distinct signer"):
            compare_observer_views([a, b], self.trusted)

    def test_fault_domain_quorum_enforced(self):
        a = self.cp("a", 1, "a" * 64)
        b = self.cp("b", 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "fault-domain"):
            compare_observer_views([a, b], self.trusted, signer_fault_domains=self.domains,
                                   minimum_fault_domains=3)

    def test_missing_domain_rejected(self):
        a = self.cp("a", 1, "a" * 64)
        b = self.cp("b", 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "missing fault-domain"):
            compare_observer_views([a, b], self.trusted, signer_fault_domains={"a": "cloud-1"})

    def test_untrusted_checkpoint_rejected(self):
        a = self.cp("a", 1, "a" * 64)
        untrusted_key = Ed25519PrivateKey.generate()
        b = sign_checkpoint(checkpoint_body("registry-log", 1, "a" * 64), "outsider", untrusted_key)
        with self.assertRaisesRegex(ValueError, "valid signatures"):
            compare_observer_views([a, b], self.trusted)

    def test_invalid_quorum_rejected(self):
        a = self.cp("a", 1, "a" * 64)
        with self.assertRaises(ValueError):
            compare_observer_views([a], self.trusted, minimum_distinct_signers=0)

    def test_multiple_fault_domains_require_mapping(self):
        a = self.cp("a", 1, "a" * 64)
        b = self.cp("b", 1, "a" * 64)
        with self.assertRaisesRegex(ValueError, "mapping is required"):
            compare_observer_views([a, b], self.trusted, minimum_fault_domains=2)


if __name__ == "__main__":
    unittest.main()
