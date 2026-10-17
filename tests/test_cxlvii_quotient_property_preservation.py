import unittest
from cxlvii_quotient_property_preservation import audit_state_property, property_on_quotient


class QuotientPropertyPreservationTests(unittest.TestCase):
    def test_property_constant_on_each_block_is_preserved(self):
        blocks = (("a", "b"), ("c", "d"))
        audit = audit_state_property(blocks, lambda s: s in {"c", "d"})
        self.assertTrue(audit.preserved)
        self.assertEqual(audit.quotient_values, (False, True))
        self.assertEqual(audit.conflict_count, 0)

    def test_mixed_block_returns_counterexample(self):
        audit = audit_state_property((("safe", "unsafe"),), lambda s: s == "unsafe")
        self.assertFalse(audit.preserved)
        self.assertEqual(audit.conflict_count, 1)
        c = audit.conflicts[0]
        self.assertEqual((c.left_state, c.right_state), ("safe", "unsafe"))
        self.assertEqual((c.left_value, c.right_value), (False, True))
        self.assertEqual(audit.quotient_values, (None,))

    def test_induced_property_rejects_mixed_block(self):
        with self.assertRaisesRegex(ValueError, "not quotient-invariant"):
            property_on_quotient((("safe", "unsafe"),), lambda s: s == "unsafe")

    def test_observation_derived_property_survives_matching_blocks(self):
        obs = {"a": "green", "b": "green", "c": "red"}
        blocks = (("a", "b"), ("c",))
        fn = lambda s: obs[s] == "red"
        self.assertTrue(audit_state_property(blocks, fn).preserved)
        self.assertEqual(property_on_quotient(blocks, fn), (False, True))

    def test_hidden_unsafe_flag_is_not_preserved_by_coarse_block(self):
        unsafe = {"s0": False, "s1": True, "s2": False}
        audit = audit_state_property((("s0", "s1"), ("s2",)), lambda s: unsafe[s])
        self.assertFalse(audit.preserved)
        self.assertEqual(audit.conflicts[0].block_index, 0)

    def test_empty_block_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            audit_state_property(((),), lambda _: False)


if __name__ == "__main__":
    unittest.main()
