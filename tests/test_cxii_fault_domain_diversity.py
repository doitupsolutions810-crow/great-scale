import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from observer_checkpoint_consistency import checkpoint_body, sign_checkpoint
from cxi_independent_witness_gossip import sign_observation
from cxii_fault_domain_diversity import analyze_fault_domains

class FaultDomainDiversityTests(unittest.TestCase):
    def setUp(self):
        self.log=Ed25519PrivateKey.generate()
        self.logtrust={"log":self.log.public_key()}
        self.keys={f"o{i}":Ed25519PrivateKey.generate() for i in range(4)}
        self.trust={k:v.public_key() for k,v in self.keys.items()}
        self.domains={"o0":"cloud-a","o1":"cloud-a","o2":"cloud-b","o3":"cloud-c"}
    def receipt(self, observer, head="a"*64, size=7):
        cp=sign_checkpoint(checkpoint_body("log",size,head),"log",self.log)
        return sign_observation(observer,cp,self.keys[observer])
    def run_analysis(self, receipts, **kw):
        args={"receipts":receipts,"trusted_observers":self.trust,"trusted_log_signers":self.logtrust,"observer_domains":self.domains}
        args.update(kw)
        return analyze_fault_domains(**args)
    def test_three_observers_two_domains_pass(self):
        r=self.run_analysis([self.receipt("o0"),self.receipt("o1"),self.receipt("o2")])
        self.assertEqual(r["status"],"DIVERSITY_THRESHOLD_MET")
    def test_three_observers_one_domain_fail(self):
        domains={o:"same" for o in self.keys}
        r=self.run_analysis([self.receipt("o0"),self.receipt("o1"),self.receipt("o3")],observer_domains=domains)
        self.assertEqual(r["status"],"INSUFFICIENT_DIVERSITY")
    def test_duplicate_identity_not_double_counted(self):
        receipt=self.receipt("o0")
        r=self.run_analysis([receipt,receipt])
        self.assertEqual(r["verified_observer_count"],1)
    def test_missing_domain_fails_closed(self):
        domains={"o0":"a","o1":"b"}
        r=self.run_analysis([self.receipt("o0"),self.receipt("o1")],observer_domains=domains,minimum_observers=2,minimum_domains=2)
        self.assertEqual(r["status"],"INSUFFICIENT_DIVERSITY")
    def test_fork_takes_precedence(self):
        r=self.run_analysis([self.receipt("o0","a"*64),self.receipt("o1","b"*64),self.receipt("o2","a"*64)])
        self.assertEqual(r["status"],"FORK_DETECTED")
    def test_untrusted_receipt_not_counted(self):
        receipt=self.receipt("o0")
        r=self.run_analysis([receipt],trusted_observers={})
        self.assertEqual(r["verified_observer_count"],0)
    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError):
            self.run_analysis([],minimum_domains=0)
    def test_three_same_domain_is_not_independence_proof(self):
        domains={o:"same" for o in self.keys}
        r=self.run_analysis([self.receipt("o0"),self.receipt("o1"),self.receipt("o3")],observer_domains=domains)
        self.assertFalse(r["domain_threshold_met"])

if __name__ == "__main__": unittest.main()
