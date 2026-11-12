import copy
import unittest
from auditable_evidence_trace import build_auditable_trace, verify_auditable_trace

class AuditableTraceTests(unittest.TestCase):
    def test_valid_trace_verifies(self):
        trace = build_auditable_trace([1, 0, 1], 0.5, lambda h: 0.5 if len(h) % 2 == 0 else 1.0)
        result = verify_auditable_trace(trace)
        self.assertTrue(result['valid'], result)
        self.assertEqual(result['observations_verified'], 3)
        self.assertAlmostEqual(result['final_wealth'], 0.78125)

    def test_outcome_tampering_detected(self):
        trace = build_auditable_trace([1, 0], 0.5, lambda h: 0.5)
        trace['records'][1]['outcome'] = 0
        self.assertFalse(verify_auditable_trace(trace)['valid'])

    def test_bet_tampering_detected(self):
        trace = build_auditable_trace([1], 0.5, lambda h: 0.5)
        trace['records'][0]['lambda'] = 0.75
        self.assertFalse(verify_auditable_trace(trace)['valid'])

    def test_reordering_detected(self):
        trace = build_auditable_trace([1, 0], 0.5, lambda h: 0.5)
        trace['records'][0], trace['records'][1] = trace['records'][1], trace['records'][0]
        self.assertFalse(verify_auditable_trace(trace)['valid'])

    def test_invalid_bet_rejected(self):
        with self.assertRaises(ValueError): build_auditable_trace([1], 0.5, lambda h: 2.1)

    def test_invalid_q0_rejected(self):
        with self.assertRaises(ValueError): build_auditable_trace([1], 0, lambda h: 0.5)

if __name__ == '__main__': unittest.main()
