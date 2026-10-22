import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from registry_transition_chain import create_transition, verify_transition, apply_transition, verify_transition_chain

class RegistryTransitionTests(unittest.TestCase):
    def setUp(self):
        self.key=Ed25519PrivateKey.generate()
        self.keys={"admin":self.key.public_key()}
        self.t1=create_transition(None,1,{"a":"domain-a","b":"domain-b"},"admin",self.key)
        self.r1=apply_transition(self.t1,None,self.keys)
        self.t2=create_transition({"payload":self.r1},2,{"a":"domain-a","b":"domain-c"},"admin",self.key)
    def test_genesis_transition_valid(self): self.assertTrue(verify_transition(self.t1,None,self.keys))
    def test_next_transition_valid(self): self.assertTrue(verify_transition(self.t2,{"payload":self.r1},self.keys))
    def test_chain_reconstructs_latest_registry(self):
        result=verify_transition_chain([self.t1,self.t2],self.keys)
        self.assertEqual(result["version"],2)
        self.assertEqual(result["witness_domains"]["b"],"domain-c")
    def test_wrong_parent_rejected(self):
        self.assertFalse(verify_transition(self.t2,None,self.keys))
    def test_skipped_version_rejected(self):
        with self.assertRaisesRegex(ValueError,"advance exactly"): create_transition({"payload":self.r1},3,{"a":"x"},"admin",self.key)
    def test_tampered_registry_rejected(self):
        t={"body":dict(self.t1["body"]),"authority_id":"admin","signature":self.t1["signature"]}
        t["body"]["registry_payload"]={"schema":"great-scale-witness-registry-v1","version":1,"witness_domains":{"a":"evil"}}
        self.assertFalse(verify_transition(t,None,self.keys))
    def test_tampered_signature_rejected(self):
        t={**self.t1,"signature":"00"}
        self.assertFalse(verify_transition(t,None,self.keys))
    def test_wrong_authority_rejected(self):
        self.assertFalse(verify_transition({**self.t1,"authority_id":"other"},None,self.keys))
    def test_replay_transition_rejected_after_advancement(self):
        self.assertFalse(verify_transition(self.t1,self.r1 and {"payload":self.r1},self.keys))

if __name__ == "__main__": unittest.main()
