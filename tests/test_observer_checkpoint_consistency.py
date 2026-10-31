import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from observer_checkpoint_consistency import checkpoint_body, sign_checkpoint, verify_checkpoint, compare_checkpoints, checkpoint_id

class ObserverCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.key=Ed25519PrivateKey.generate()
        self.trusted={"log":self.key.public_key()}
    def cp(self,size,head,parent="0"*64):
        return sign_checkpoint(checkpoint_body("registry-log",size,head,parent),"log",self.key)
    def test_valid_checkpoint(self): self.assertTrue(verify_checkpoint(self.cp(1,"a"*64),self.trusted))
    def test_same_size_same_head(self): self.assertEqual(compare_checkpoints(self.cp(2,"b"*64),self.cp(2,"b"*64),self.trusted),"SAME")
    def test_same_size_different_head_is_fork(self): self.assertEqual(compare_checkpoints(self.cp(2,"b"*64),self.cp(2,"c"*64),self.trusted),"FORK")
    def test_direct_predecessor_is_ordered(self):
        first=self.cp(1,"a"*64)
        second=self.cp(2,"b"*64,checkpoint_id(first))
        self.assertEqual(compare_checkpoints(first,second,self.trusted),"ORDERED")
    def test_missing_link_is_incomparable(self): self.assertEqual(compare_checkpoints(self.cp(1,"a"*64),self.cp(2,"b"*64),self.trusted),"INCOMPARABLE")
    def test_different_log_is_incomparable(self):
        a=self.cp(1,"a"*64)
        other=sign_checkpoint(checkpoint_body("other-log",1,"a"*64),"log",self.key)
        self.assertEqual(compare_checkpoints(a,other,self.trusted),"INCOMPARABLE")
    def test_tampered_head_invalidates_signature(self):
        cp=self.cp(1,"a"*64); cp["body"]["head_hash"]="f"*64
        self.assertFalse(verify_checkpoint(cp,self.trusted))
    def test_untrusted_signer_rejected(self):
        cp=self.cp(1,"a"*64)
        self.assertFalse(verify_checkpoint(cp,{}))
    def test_invalid_size_rejected(self):
        with self.assertRaises(ValueError): checkpoint_body("x",0,"a")
    def test_wrong_schema_rejected(self):
        cp=self.cp(1,"a"*64); cp["body"]["schema"]="wrong"
        self.assertFalse(verify_checkpoint(cp,self.trusted))

if __name__ == "__main__": unittest.main()
