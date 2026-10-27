import unittest
from cxlxiv_canonical_typed_encoding import canonical_encode, encode_model, UnsupportedLabel

class Label:
    def __repr__(self): return "same-looking-label"

class CanonicalTypedEncodingTests(unittest.TestCase):
    def test_type_tags_distinguish_bool_and_int(self):
        self.assertNotEqual(canonical_encode(True),canonical_encode(1))
    def test_type_tags_distinguish_int_and_string(self):
        self.assertNotEqual(canonical_encode(12),canonical_encode("12"))
    def test_tuple_encoding_is_deterministic(self):
        self.assertEqual(canonical_encode(("x",2,False)),canonical_encode(("x",2,False)))
    def test_non_finite_float_rejected(self):
        with self.assertRaises(UnsupportedLabel): canonical_encode(float("nan"))
    def test_arbitrary_objects_rejected_instead_of_repr_fallback(self):
        with self.assertRaises(UnsupportedLabel): canonical_encode(Label())
    def test_model_encoding_has_version_and_unique_states(self):
        model=encode_model(["s1","s2"],{"s1":{"go":"s2"},"s2":{}})
        self.assertEqual(model["encoding_version"],"gs-typed-v1")
        self.assertEqual(len(model["state_ids"]),2)
        self.assertEqual(len(model["action_ids"]),1)
    def test_duplicate_state_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate canonical state"):
            encode_model(["x","x"],{"x":{}})

if __name__=="__main__": unittest.main()
