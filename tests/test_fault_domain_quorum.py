import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from threshold_witness_checkpoint import create_checkpoint
from fault_domain_quorum import verify_fault_diverse_checkpoint

class FaultDomainQuorumTests(unittest.TestCase):
    def setUp(self):
        self.private = {f"w{i}": Ed25519PrivateKey.generate() for i in range(4)}
        self.public = {w:k.public_key() for w,k in self.private.items()}
        self.domains = {"w0":"cloud-a", "w1":"cloud-a", "w2":"cloud-b", "w3":"cloud-c"}
        self.trace = {"result":"validated","n":12}
        self.cp = create_checkpoint(self.trace, 12, self.private, "anchor-11")
    def verify(self, cp=None, domains=None, threshold=3, min_domains=2):
        return verify_fault_diverse_checkpoint(cp or self.cp, self.trace, self.public, domains or self.domains, threshold, min_domains, 12, "anchor-11")
    def test_three_signatures_across_three_domains_pass(self): self.assertTrue(self.verify())
    def test_three_signatures_but_only_two_domains_fail_if_three_required(self):
        self.assertFalse(self.verify(min_domains=3))
    def test_two_signatures_fail_threshold(self):
        cp=create_checkpoint(self.trace,12,{"w0":self.private["w0"],"w2":self.private["w2"]},"anchor-11")
        self.assertFalse(self.verify(cp))
    def test_two_signatures_same_domain_fail_domain_rule(self):
        cp=create_checkpoint(self.trace,12,{"w0":self.private["w0"],"w1":self.private["w1"]},"anchor-11")
        self.assertFalse(self.verify(cp,threshold=2,min_domains=2))
    def test_tampered_signature_not_counted(self):
        cp={"statement":self.cp["statement"],"signatures":[dict(x) for x in self.cp["signatures"]]}
        cp["signatures"][0]["signature"]="00"
        self.assertFalse(self.verify(cp))
    def test_missing_domain_mapping_rejected(self):
        with self.assertRaisesRegex(ValueError,"every trusted witness"):
            self.verify(domains={"w0":"a"})
    def test_domain_count_cannot_exceed_threshold(self):
        with self.assertRaises(ValueError): self.verify(threshold=2,min_domains=3)
    def test_duplicate_witness_rejected(self):
        cp={"statement":self.cp["statement"],"signatures":list(self.cp["signatures"])}
        cp["signatures"].append(dict(cp["signatures"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate"): self.verify(cp)
    def test_wrong_trace_rejected(self):
        self.assertFalse(verify_fault_diverse_checkpoint(self.cp,{"result":"changed"},self.public,self.domains,3,2,12,"anchor-11"))
    def test_empty_domain_rejected(self):
        domains=dict(self.domains); domains["w1"]=" "
        with self.assertRaisesRegex(ValueError,"non-empty"): self.verify(domains=domains)

if __name__ == "__main__": unittest.main()
