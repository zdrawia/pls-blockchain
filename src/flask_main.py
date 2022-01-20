# from db import cas
# import fog_server
# import sequencer
# import logging
# import things
# from src.db.mt import MerkleTree
#
# logging.basicConfig(level=logging.DEBUG)
# cas = cas.CAS()
# fog_server = fog_server.FogServer()
# thing = things.Thing(fog_server)
# sequencer = sequencer.Sequencer([thing])
# # thing.enroll()
# # thing.post("hi")
# # thing.post("ok")
#
#
# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def hello_world():
#     return '"/enroll" - to enroll new thing, "/post/<message>" - to post message in chain, "/show" - show chain'
#
#
# @app.route('/enroll')
# def enroll():
#     return "Enrolled thing with ID = " + thing.enroll()
#
#
# @app.route('/post/<message>')
# def post_message(message):
#     return thing.post(message)
#
#
# @app.route('/show')
# def show():
#     res = ""
#     for block in fog_server.blocks:
#         res += block.tree.value_hash + "///////////////////"
#     return res
#
#
# if __name__ == '__main__':
#     app.run()
