import unittest
from cxlxii_quotient_certificate import make_certificate, verify_certificate
from cxlxiii_adversarial_certificate_testing import reference_partition, audit_model

class SameRepr:
    def __init__(self,value): self.value=value
    def __repr__(self): return "collision"

class AdversarialCertificateTests(unittest.TestCase):
    def model(self):
        states=["a","b","c","d"]
        obs={"a":"x","b":"x","c":"y","d":"y"}
        props={s:(obs[s]=="y",) for s in states}
        edges={"a":{"go":"c"},"b":{"go":"d"},"c":{},"d":{}}
        return states,obs,props,edges
    def test_independent_oracle_agrees_on_canonical_partition(self):
        s,o,p,e=self.model(); part=[{"a","b"},{"c","d"}]
        report=audit_model(s,o,p,e,part)
        self.assertTrue(report["verifier_valid"]); self.assertTrue(report["oracle_match"])
    def test_oracle_detects_over_split(self):
        s,o,p,e=self.model(); part=[{"a"},{"b"},{"c"},{"d"}]
        report=audit_model(s,o,p,e,part)
        self.assertFalse(report["verifier_valid"]); self.assertFalse(report["oracle_match"])
    def test_state_repr_collision_fails_closed(self):
        a,b=SameRepr(1),SameRepr(2); states=[a,b]
        with self.assertRaisesRegex(ValueError,"state repr keys"):
            make_certificate(states,{a:"x",b:"x"},{a:(),b:()},{a:{},b:{}},[{a,b}])
    def test_action_repr_collision_fails_closed(self):
        a,b="s","t"; x,y=SameRepr(1),SameRepr(2)
        with self.assertRaisesRegex(ValueError,"action repr keys"):
            make_certificate([a,b],{a:"x",b:"x"},{a:(),b:()},{a:{x:b},b:{y:a}},[{a,b}])
    def test_tampered_mapping_is_rejected(self):
        s,o,p,e=self.model(); part=[{"a","b"},{"c","d"}]
        cert=make_certificate(s,o,p,e,part); cert["state_to_block"]["a"]=999
        self.assertFalse(verify_certificate(s,o,p,e,part,cert)["valid"])
    def test_transition_mutation_invalidates_quotient(self):
        s,o,p,e=self.model(); part=[{"a","b"},{"c","d"}]
        changed={**e,"b":{"go":"b"}}; cert=make_certificate(s,o,p,changed,part)
        self.assertFalse(verify_certificate(s,o,p,changed,part,cert)["valid"])

if __name__=="__main__": unittest.main()
