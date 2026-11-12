import unittest
from great_scale.provenance_closure import ProvenanceGraph, Certificate, Status

class ProvenanceClosureTests(unittest.TestCase):
    def graph(self):
        g=ProvenanceGraph()
        g.add(Certificate('calibration',1))
        g.add(Certificate('measurement',1,('calibration',)))
        g.add(Certificate('forecast',1,('measurement',)))
        g.add(Certificate('independent_check',1))
        return g
    def test_revocation_propagates_transitively(self):
        g=self.graph(); affected=g.revoke_root('calibration')
        self.assertEqual(affected,['calibration','measurement','forecast'])
        self.assertEqual(g.certificates['calibration'].status,Status.INVALID)
        self.assertEqual(g.certificates['measurement'].status,Status.STALE)
        self.assertEqual(g.certificates['forecast'].status,Status.STALE)
    def test_independent_branch_remains_valid(self):
        g=self.graph(); g.revoke_root('calibration')
        self.assertEqual(g.certificates['independent_check'].status,Status.VALID)
    def test_revalidation_requires_dependencies_valid(self):
        g=self.graph(); g.revoke_root('calibration')
        with self.assertRaises(ValueError): g.revalidate('measurement',2,'rechecked')
    def test_bottom_up_revalidation_restores_chain(self):
        g=self.graph(); g.revoke_root('calibration')
        g.revalidate('calibration',2,'new independent calibration')
        g.revalidate('measurement',2,'recomputed against v2')
        g.revalidate('forecast',2,'recomputed from measurement v2')
        self.assertTrue(all(c.status is Status.VALID for c in g.certificates.values()))
    def test_duplicate_id_rejected(self):
        g=self.graph()
        with self.assertRaises(ValueError): g.add(Certificate('calibration',2))
    def test_unknown_dependency_rejected(self):
        g=ProvenanceGraph()
        with self.assertRaises(ValueError): g.add(Certificate('x',1,('missing',)))
    def test_unknown_revoke_rejected(self):
        with self.assertRaises(KeyError): ProvenanceGraph().revoke_root('missing')
    def test_invalid_version_rejected(self):
        g=self.graph()
        with self.assertRaises(ValueError): g.revalidate('calibration',0,'bad')

if __name__ == '__main__': unittest.main()
