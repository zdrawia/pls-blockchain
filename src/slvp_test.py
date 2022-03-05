import logging
import unittest

import fog_server
import sequencer
import things
from src.db.cas import CAS


class TestSLVP(unittest.TestCase):
    def test_post(self):
        blocks_hashes = ['00ff278e2bb68384339ffe69ae324d188295ca47b50b4f20e0b6aed2b66dc5c6',
                         'a0bd53bcce0ca557fd3f2ad70d0e824076c20748abd586548c80f1582e56967d',
                         '5afc64b0c7081c7f21a78e3b6b27fc53b9aa8da7734ebf249fff46dc86555f28']
        cas = CAS()
        fogserver = fog_server.FogServer(cas)
        seq = sequencer.Sequencer()
        seq.blocks_hashes = blocks_hashes
        thing = things.Thing(fogserver, seq)
        seq.things = [thing]
        thing.enroll()
        seq.broadcast()
        seq.broadcast()
        thing.post()
        thing.post()

if __name__ == '__main__':
    unittest.main()
