from flask import Flask
from flask import jsonify
from flask import request
import jsonpickle
from fog_server import FogServer
from db.cas import CAS

app = Flask(__name__)

cas = CAS()
server = FogServer(cas)


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})


@app.route('/enroll', methods=['POST'])
def enroll():
    enroll_message_json = request.get_json()
    enroll_message = jsonpickle.decode(enroll_message_json)
    identifier = server.receive(enroll_message)
    return jsonify({'message': identifier})


@app.route('/post', methods=['POST'])
def post():
    post_message_json = request.get_json()
    post_message = jsonpickle.decode(post_message_json)
    server.receive(post_message)


@app.route('/generatekey', methods=['GET'])
def gen_key():
    key = server.generate_key()
    return jsonify({'message': key})


@app.route('/getblocks', methods=['GET'])
def get_blocks():
    blocks = jsonpickle.encode(server.cas.blocks)
    return jsonify({'message': blocks})


if __name__ == "__main__":
    app.run()
