import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from external_anchor_witness import create_anchor_statement, sign_anchor, verify_anchor

class ExternalAnchorTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.public = self.private.public_key()
        self.trace = {"final_hash": "a" * 64, "observations": [1, 0, 1]}
        self.statement = create_anchor_statement(self.trace, 1)
        self.anchor = sign_anchor(self.statement, self.private)

    def test_valid_anchor(self):
        self.assertTrue(verify_anchor(self.anchor, self.public, self.trace, 1)["valid"])

    def test_modified_trace_rejected(self):
        altered = {**self.trace, "observations": [0, 0, 1]}
        self.assertFalse(verify_anchor(self.anchor, self.public, altered, 1)["valid"])

    def test_modified_signature_rejected(self):
        altered = copy.deepcopy(self.anchor)
        altered["signature_hex"] = "00" * 64
        self.assertFalse(verify_anchor(altered, self.public, self.trace, 1)["valid"])

    def test_wrong_sequence_rejected(self):
        self.assertFalse(verify_anchor(self.anchor, self.public, self.trace, 2)["valid"])

    def test_wrong_predecessor_rejected(self):
        self.assertFalse(verify_anchor(self.anchor, self.public, self.trace, 1, "b" * 64)["valid"])

if __name__ == "__main__": unittest.main()
