import unittest
from scoped_evidence_certificate import build_evidence_certificate

class ScopedEvidenceCertificateTests(unittest.TestCase):
    def cert(self, **overrides):
        args = dict(state_equivalence="MATCH", lineage_relation="SAME", observed_count=3,
            declared_count=3, scope_complete=True, authenticity_status="VERIFIED",
            distinct_signers=2, signer_threshold=2, trust_basis="verified by upstream Ed25519 policy",
            evidence_ids=["a", "b", "c"], assumptions=["trusted registry is correct"])
        args.update(overrides)
        return build_evidence_certificate(**args)

    def test_complete_trusted_matching_evidence_is_scoped_consistent(self):
        self.assertEqual(self.cert()["disposition"], "CONSISTENT_WITHIN_DECLARED_SCOPE")
    def test_equal_state_but_incomparable_lineage_is_unresolved(self):
        self.assertEqual(self.cert(lineage_relation="INCOMPARABLE")["disposition"], "UNRESOLVED")
    def test_fork_dominates_incomplete_population(self):
        self.assertEqual(self.cert(lineage_relation="FORK", observed_count=2, declared_count=3, scope_complete=False)["disposition"], "CONFLICT_WITHIN_OBSERVED_EVIDENCE")
    def test_incomplete_population_never_certifies_global_consistency(self):
        self.assertEqual(self.cert(observed_count=2, declared_count=3, scope_complete=False)["disposition"], "PARTIAL_EVIDENCE")
    def test_unverified_authenticity_blocks_consistency(self):
        self.assertEqual(self.cert(authenticity_status="UNVERIFIED")["disposition"], "UNRESOLVED")
    def test_state_mismatch_is_conflict_not_silent_consistency(self):
        self.assertEqual(self.cert(state_equivalence="MISMATCH")["disposition"], "CONFLICT_WITHIN_OBSERVED_EVIDENCE")
    def test_complete_requires_declared_population_match(self):
        with self.assertRaises(ValueError): self.cert(observed_count=2, declared_count=3, scope_complete=True)
    def test_verified_requires_threshold_and_basis(self):
        with self.assertRaises(ValueError): self.cert(distinct_signers=1)
        with self.assertRaises(ValueError): self.cert(trust_basis="")
    def test_duplicate_evidence_ids_rejected(self):
        with self.assertRaises(ValueError): self.cert(evidence_ids=["a", "a", "c"])
    def test_unknown_lineage_never_certifies(self):
        self.assertEqual(self.cert(lineage_relation="NOT_ASSESSED")["disposition"], "UNRESOLVED")

if __name__ == "__main__":
    unittest.main()
