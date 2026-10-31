import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from registry_provenance import create_signed_registry, verify_signed_registry, create_registry_bound_checkpoint, verify_registry_bound_checkpoint

class RegistryProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.authority=Ed25519PrivateKey.generate()
        self.authority_pub={"registry-admin":self.authority.public_key()}
        self.private={f"w{i}":Ed25519PrivateKey.generate() for i in range(3)}
        self.public={w:k.public_key() for w,k in self.private.items()}
        self.domains={"w0":"domain-a","w1":"domain-b","w2":"domain-c"}
        self.registry=create_signed_registry(4,self.domains,"registry-admin",self.authority)
        self.trace={"measurements":[1,2,3]}
        self.cp=create_registry_bound_checkpoint(self.trace,21,"anchor-20",self.registry,self.private)
    def verify(self, cp=None, registry=None, required=4, trace=None):
        return verify_registry_bound_checkpoint(cp or self.cp,self.trace if trace is None else trace,registry or self.registry,self.authority_pub,self.public,2,21,"anchor-20",required)
    def test_valid_registry_and_checkpoint(self): self.assertTrue(self.verify())
    def test_registry_signature_validates(self): self.assertTrue(verify_signed_registry(self.registry,self.authority_pub))
    def test_registry_payload_tamper_rejected(self):
        reg={**self.registry,"payload":{**self.registry["payload"],"witness_domains":{**self.domains,"w0":"domain-z"}}}
        self.assertFalse(self.verify(registry=reg))
    def test_wrong_registry_version_rejected(self): self.assertFalse(self.verify(required=5))
    def test_checkpoint_registry_hash_tamper_rejected(self):
        cp={"statement":dict(self.cp["statement"]),"signatures":list(self.cp["signatures"])}
        cp["statement"]["registry_hash"]="00"
        self.assertFalse(self.verify(cp=cp))
    def test_wrong_trace_rejected(self): self.assertFalse(self.verify(trace={"measurements":[9]}))
    def test_unregistered_witness_does_not_count(self):
        private={"x":Ed25519PrivateKey.generate()}
        cp=create_registry_bound_checkpoint(self.trace,21,"anchor-20",self.registry,private)
        pub={"x":private["x"].public_key(),**self.public}
        self.assertFalse(verify_registry_bound_checkpoint(cp,self.trace,self.registry,self.authority_pub,pub,1,21,"anchor-20",4))
    def test_registry_version_must_be_positive(self):
        with self.assertRaises(ValueError): create_signed_registry(0,self.domains,"registry-admin",self.authority)
    def test_duplicate_signer_rejected(self):
        cp={"statement":self.cp["statement"],"signatures":list(self.cp["signatures"])}
        cp["signatures"].append(dict(cp["signatures"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate"): self.verify(cp=cp)
    def test_registry_requires_nonempty_domains(self):
        with self.assertRaises(ValueError): create_signed_registry(5,{"w0":" "},"registry-admin",self.authority)

if __name__ == "__main__": unittest.main()
