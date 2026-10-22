import unittest
from cxlxii_quotient_certificate import make_certificate, verify_certificate

class QuotientCertificateTests(unittest.TestCase):
    def setUp(self):
        self.states=["a","b","c"]
        self.obs={"a":"x","b":"x","c":"y"}
        self.props={"a":(False,),"b":(False,),"c":(True,)}
        self.edges={"a":{"go":"c"},"b":{"go":"c"},"c":{}}
        self.good=[{"a","b"},{"c"}]
        self.cert=make_certificate(self.states,self.obs,self.props,self.edges,self.good)

    def test_accepts_canonical_certificate(self):
        result=verify_certificate(self.states,self.obs,self.props,self.edges,self.good,self.cert)
        self.assertTrue(result["valid"])
        self.assertTrue(result["sound"])
        self.assertTrue(result["minimal"])

    def test_rejects_over_split_partition_as_nonminimal(self):
        p=[{"a"},{"b"},{"c"}]
        cert=make_certificate(self.states,self.obs,self.props,self.edges,p)
        result=verify_certificate(self.states,self.obs,self.props,self.edges,p,cert)
        self.assertFalse(result["valid"])
        self.assertFalse(result["minimal"])

    def test_rejects_coarse_partition_with_different_observations(self):
        p=[{"a","b","c"}]
        cert=make_certificate(self.states,self.obs,self.props,self.edges,p)
        result=verify_certificate(self.states,self.obs,self.props,self.edges,p,cert)
        self.assertFalse(result["sound"])

    def test_rejects_tampered_certificate(self):
        bad={**self.cert,"block_count":99}
        result=verify_certificate(self.states,self.obs,self.props,self.edges,self.good,bad)
        self.assertFalse(result["valid"])

    def test_rejects_incomplete_partition(self):
        p=[{"a","b"}]
        cert={"state_to_block":{"a":0,"b":0},"block_count":1,"state_count":2}
        result=verify_certificate(self.states,self.obs,self.props,self.edges,p,cert)
        self.assertFalse(result["valid"])

    def test_rejects_invalid_transition(self):
        edges={**self.edges,"a":{"go":"missing"}}
        with self.assertRaises(ValueError):
            verify_certificate(self.states,self.obs,self.props,edges,self.good,self.cert)

if __name__=="__main__": unittest.main()
