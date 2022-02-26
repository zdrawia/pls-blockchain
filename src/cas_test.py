import hashlib
import unittest
from db.cas import CAS
from db.blocks import Block
from db import mt


class TestCAS(unittest.TestCase):
    def test_deploy(self):
        cas = CAS()
        hash_val = cas.deploy("hi")
        self.assertEqual(hash_val, hashlib.sha256("hi".encode()).hexdigest())

    def test_retrieve(self):
        cas = CAS()
        hash_val = cas.deploy("hi")
        self.assertEqual("hi", cas.retrieve(hash_val))

    def test_contrib(self):
        cas = CAS()
        values = ["Hi", "Hello", "New", "Value"]
        data = {
            "0x11": "contrib1",
            "0x22": "contrib2",
            "0x33": "contrib3",
            "0x44": "contrib4"
        }
        block = Block(74, mt.MerkleTree.generate_tree(values), data)
        cas.blocks = [block]
        ca = cas.get_contrib(74, ["0x11", "0x33"])
        val = (['contrib1', 'contrib3'],
               ['fc3d5a0a5e0754d4f2d6f8c8abb3d4806201c955a1ea2bd0851d465eb7404a51',
                'bc5eb87a5ba869c78ea6012bf10a0901877c502807c26f671d69ff4d264383b6',
                'bcf1513dc62f205f16f9c4525984ddab9725363b30c8b92146281b8f03e30150',
                '3639efcd08abb273b1619e82e78c29a7df02c1051b1820e99fc395dcaa3326b8',
                '185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969',
                '18fdd549b2ed367ac0c74cbec1214644728515b30edbcb78e7d322757a7c8359',
                '8e37953d23daca5ff01b8282c33f4e0a2152f1d1885f94c06418617e3ee1d24e'])
        self.assertEqual(ca, val)
