import unittest
from evidence_scope_binding import build_scope_manifest, evaluate_scope_binding


class EvidenceScopeBindingTests(unittest.TestCase):
    def manifest(self, **overrides):
        args = dict(scope_id="release-2026-10", declared_evidence_ids=["ev-a", "ev-b", "ev-c"],
                    policy_id="checkpoint-consistency", policy_version="2",
                    authority_ref="registry://trusted-manifest")
        args.update(overrides)
        return build_scope_manifest(**args)

    def test_exact_manifest_match_is_only_relative_to_manifest(self):
        result = evaluate_scope_binding(self.manifest(), ["ev-c", "ev-a", "ev-b"])
        self.assertEqual(result["status"], "EXACT_MANIFEST_MATCH")
        self.assertFalse(result["external_completeness_proven"])

    def test_missing_declared_item_is_partial(self):
        result = evaluate_scope_binding(self.manifest(), ["ev-a", "ev-b"])
        self.assertEqual(result["status"], "PARTIAL_SCOPE")
        self.assertEqual(result["missing_ids"], ["ev-c"])

    def test_extra_item_is_scope_mismatch(self):
        result = evaluate_scope_binding(self.manifest(), ["ev-a", "ev-b", "ev-c", "ev-x"])
        self.assertEqual(result["status"], "SCOPE_MISMATCH")
        self.assertEqual(result["extra_ids"], ["ev-x"])

    def test_manifest_order_does_not_change_digest(self):
        a = self.manifest(declared_evidence_ids=["ev-a", "ev-b", "ev-c"])
        b = self.manifest(declared_evidence_ids=["ev-c", "ev-b", "ev-a"])
        self.assertEqual(a["manifest_digest"], b["manifest_digest"])

    def test_manifest_tampering_is_detected(self):
        manifest = self.manifest()
        manifest["declared_evidence_ids"][0] = "ev-forged"
        result = evaluate_scope_binding(manifest, ["ev-a", "ev-b", "ev-c"])
        self.assertEqual(result["status"], "INVALID_MANIFEST")

    def test_declared_count_tampering_is_detected(self):
        manifest = self.manifest()
        manifest["declared_count"] = 99
        result = evaluate_scope_binding(manifest, ["ev-a", "ev-b", "ev-c"])
        self.assertEqual(result["status"], "INVALID_MANIFEST")

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            self.manifest(declared_evidence_ids=["ev-a", "ev-a"])

    def test_empty_scope_rejected(self):
        with self.assertRaises(ValueError):
            self.manifest(declared_evidence_ids=[])

    def test_scope_and_policy_identity_are_digest_bound(self):
        original = self.manifest()
        changed = dict(original)
        changed["policy_version"] = "3"
        result = evaluate_scope_binding(changed, ["ev-a", "ev-b", "ev-c"])
        self.assertEqual(result["status"], "INVALID_MANIFEST")

    def test_boolean_count_is_not_accepted_as_integer_count(self):
        manifest = self.manifest(declared_evidence_ids=["only-one"])
        manifest["declared_count"] = True
        self.assertEqual(evaluate_scope_binding(manifest, ["only-one"])["status"], "INVALID_MANIFEST")

    def test_non_string_observation_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_scope_binding(self.manifest(), ["ev-a", 5, "ev-c"])


if __name__ == "__main__":
    unittest.main()
