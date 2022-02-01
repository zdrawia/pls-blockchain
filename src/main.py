from db import cas
import fog_server
import sequencer
import logging
import things

logging.basicConfig(level=logging.DEBUG)
# fog_server = fog_server.FogServer()
# thing = things.Thing(fog_server)
# sequencer = sequencer.Sequencer([thing])
# thing.enroll()
# sequencer.broadcast()
# sequencer.broadcast()
cas = cas.CAS()
val = cas.deploy("hi!!")
print("Hashed = " + val)
print("Retrieved = " + cas.retrieve(val))

from db import blocks
from db import mt
values = ["Hi", "Hello", "New", "Value"]
data = {
    "0x11": "contrib1",
    "0x22": "contrib2",
    "0x33": "contrib3",
    "0x44": "contrib4"
}
block = blocks.Block(74, mt.MerkleTree.generate_tree(values), data)
cas.blocks = [block]
ca = cas.get_contrib(74, ["0x11", "0x33"])
print(f"get_contrib() = {ca}")
