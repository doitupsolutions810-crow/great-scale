import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from threshold_witness_checkpoint import create_checkpoint, verify_checkpoint

class ThresholdWitnessTests(unittest.TestCase):
    def setUp(self):
        self.private = {f"w{i}": Ed25519PrivateKey.generate() for i in range(3)}
        self.public = {name: key.public_key() for name, key in self.private.items()}
        self.trace = {"events": [{"step": 1, "value": 0.7}]}
        self.checkpoint = create_checkpoint(self.trace, 8, self.private, "prior-7")
    def verify(self, checkpoint=None, trace=None, threshold=2, sequence=8, previous="prior-7"):
        return verify_checkpoint(checkpoint or self.checkpoint, self.trace if trace is None else trace, self.public, threshold, sequence, previous)
    def test_threshold_met(self): self.assertTrue(self.verify())
    def test_threshold_not_met(self):
        cp = create_checkpoint(self.trace, 8, {"w0": self.private["w0"]}, "prior-7")
        self.assertFalse(self.verify(cp))
    def test_changed_trace_rejected(self): self.assertFalse(self.verify(trace={"events": []}))
    def test_wrong_sequence_rejected(self): self.assertFalse(self.verify(sequence=9))
    def test_wrong_predecessor_rejected(self): self.assertFalse(self.verify(previous="other"))
    def test_tampered_signature_does_not_count(self):
        cp = {"statement": self.checkpoint["statement"], "signatures": [dict(s) for s in self.checkpoint["signatures"]]}
        cp["signatures"][0]["signature"] = "00"
        self.assertTrue(self.verify(cp))
    def test_duplicate_identity_rejected(self):
        cp = {"statement": self.checkpoint["statement"], "signatures": list(self.checkpoint["signatures"])}
        cp["signatures"].append(dict(cp["signatures"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"): self.verify(cp)
    def test_unknown_witness_does_not_count(self):
        cp = create_checkpoint(self.trace, 8, {"w0": self.private["w0"]}, "prior-7")
        cp["signatures"].append({"witness_id": "untrusted", "signature": "00"})
        self.assertFalse(self.verify(cp))
    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError): self.verify(threshold=0)

if __name__ == "__main__": unittest.main()
