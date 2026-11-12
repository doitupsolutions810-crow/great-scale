import unittest
from cxlviii_property_guided_refinement import refine_partition_by_properties


class PropertyGuidedRefinementTests(unittest.TestCase):
    def test_splits_safe_and_unsafe_states(self):
        report = refine_partition_by_properties(
            (("safe", "unsafe", "unknown"),),
            (lambda s: s == "unsafe",),
        )
        self.assertEqual(report.final_block_count, 2)
        self.assertEqual(report.split_count, 1)
        self.assertTrue(report.properties_preserved)
        self.assertEqual({s for block in report.blocks for s in block},
                         {"safe", "unsafe", "unknown"})
        self.assertTrue(all(len({s == "unsafe" for s in block}) == 1
                            for block in report.blocks))

    def test_joint_signature_splits_for_multiple_properties(self):
        props = (lambda s: s[0] == "unsafe", lambda s: s[1] == "terminal")
        report = refine_partition_by_properties(
            ((("safe", "live"), ("unsafe", "live"),
              ("safe", "terminal"), ("unsafe", "terminal")),), props)
        self.assertEqual(report.final_block_count, 4)
        self.assertTrue(report.properties_preserved)

    def test_already_constant_partition_does_not_split(self):
        report = refine_partition_by_properties(
            (("safe1", "safe2"), ("unsafe1",)),
            (lambda s: s.startswith("unsafe"),),
        )
        self.assertEqual(report.final_block_count, 2)
        self.assertEqual(report.split_count, 0)

    def test_no_properties_leaves_partition_unchanged(self):
        report = refine_partition_by_properties((("a", "b"), ("c",)), ())
        self.assertEqual(report.blocks, (("a", "b"), ("c",)))
        self.assertTrue(report.properties_preserved)

    def test_empty_block_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            refine_partition_by_properties(((),), (lambda _: True,))

    def test_duplicate_state_rejected(self):
        with self.assertRaisesRegex(ValueError, "more than once"):
            refine_partition_by_properties((("a", "b"), ("b",)), (lambda _: True,))


if __name__ == "__main__":
    unittest.main()
