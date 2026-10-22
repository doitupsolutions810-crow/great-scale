import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from observer_checkpoint_consistency import checkpoint_body, sign_checkpoint
from cxi_independent_witness_gossip import sign_observation, verify_observation, analyze_observations

class IndependentWitnessGossipTests(unittest.TestCase):
    def setUp(self):
        self.logkey=Ed25519PrivateKey.generate()
        self.logtrust={"log":self.logkey.public_key()}
        self.observers={f"o{i}":Ed25519PrivateKey.generate() for i in range(3)}
        self.observertrust={k:v.public_key() for k,v in self.observers.items()}
    def cp(self, head, size=4):
        return sign_checkpoint(checkpoint_body("registry",size,head),"log",self.logkey)
    def receipt(self, observer, cp):
        return sign_observation(observer,cp,self.observers[observer])
    def test_valid_receipt(self):
        self.assertTrue(verify_observation(self.receipt("o0",self.cp("a"*64)),self.observertrust,self.logtrust))
    def test_bad_observer_signature_rejected(self):
        r=self.receipt("o0",self.cp("a"*64)); r["signature"]="00"
        self.assertFalse(verify_observation(r,self.observertrust,self.logtrust))
    def test_two_observers_same_view_no_conflict(self):
        cp=self.cp("a"*64)
        result=analyze_observations([self.receipt("o0",cp),self.receipt("o1",cp)],self.observertrust,self.logtrust,2)
        self.assertEqual(result["status"],"NO_CONFLICT_OBSERVED")
    def test_conflicting_views_detected(self):
        result=analyze_observations([self.receipt("o0",self.cp("a"*64)),self.receipt("o1",self.cp("b"*64))],self.observertrust,self.logtrust,2)
        self.assertEqual(result["status"],"FORK_DETECTED")
        self.assertEqual(len(result["conflicts"]),1)
    def test_one_observer_is_insufficient(self):
        result=analyze_observations([self.receipt("o0",self.cp("a"*64))],self.observertrust,self.logtrust,2)
        self.assertEqual(result["status"],"INSUFFICIENT_OBSERVERS")
    def test_untrusted_observer_rejected(self):
        r=self.receipt("o0",self.cp("a"*64))
        self.assertFalse(verify_observation(r,{},self.logtrust))
    def test_tampered_checkpoint_rejected(self):
        r=self.receipt("o0",self.cp("a"*64)); r["body"]["checkpoint"]["body"]["head_hash"]="c"*64
        self.assertFalse(verify_observation(r,self.observertrust,self.logtrust))
    def test_duplicate_observer_not_counted_twice(self):
        r=self.receipt("o0",self.cp("a"*64))
        result=analyze_observations([r,r],self.observertrust,self.logtrust,2)
        self.assertEqual(result["verified_observer_count"],1)
        self.assertEqual(result["status"],"INSUFFICIENT_OBSERVERS")
    def test_invalid_minimum_rejected(self):
        with self.assertRaises(ValueError): analyze_observations([],self.observertrust,self.logtrust,0)

if __name__ == "__main__": unittest.main()
