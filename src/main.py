from db import cas
import fog_server
import sequencer
import logging
import things

logging.basicConfig(level=logging.DEBUG)
fog_server = fog_server.FogServer()
thing = things.Thing(fog_server)
sequencer = sequencer.Sequencer([thing])
thing.enroll()
sequencer.broadcast()
sequencer.broadcast()


