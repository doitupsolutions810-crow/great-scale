import unittest

from cxlvii_quotient_property_preservation import audit_state_property, property_on_quotient


class QuotientPropertyPreservationTests(unittest.TestCase):
    def test_observation_derived_property_is_constant_within_blocks(self):
        blocks = [["s0", "s1"], ["s2"]]
        observations = {"s0": "red", "s1": "red", "s2": "blue"}
        audit = audit_state_property(blocks, lambda s: observations[s] == "red")
        self.assertTrue(audit.preserved)
        self.assertEqual(audit.checked_state_count, 3)
        self.assertEqual(audit.witness_count, 0)

    def test_hidden_unsafe_flag_produces_counterexample(self):
        blocks = [["safe", "unsafe"], ["other"]]
        is_unsafe = {"safe": False, "unsafe": True, "other": False}
        audit = audit_state_property(blocks, lambda s: is_unsafe[s])
        self.assertFalse(audit.preserved)
        self.assertEqual(audit.witness_count, 1)
        self.assertEqual(audit.witnesses[0].left_state, "safe")
        self.assertEqual(audit.witnesses[0].right_state, "unsafe")

    def test_quotient_property_map_is_well_defined_when_constant(self):
        blocks = [["a", "b"], ["c"]]
        values = {"a": 2, "b": 2, "c": 7}
        mapping = property_on_quotient(blocks, lambda s: values[s])
        self.assertEqual(mapping["a"], (0, 2))
        self.assertEqual(mapping["b"], (0, 2))
        self.assertEqual(mapping["c"], (1, 7))

    def test_quotient_property_map_rejects_mixed_class(self):
        with self.assertRaisesRegex(ValueError, "not quotient-invariant"):
            property_on_quotient([["safe", "unsafe"]], lambda s: s == "unsafe")

    def test_empty_block_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            audit_state_property([[]], lambda s: True)

    def test_duplicate_state_across_blocks_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly one block"):
            audit_state_property([["a"], ["a"]], lambda s: True)


if __name__ == "__main__":
    unittest.main()
