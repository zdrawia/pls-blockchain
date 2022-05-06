from flask import Flask
from flask import jsonify
from flask import request
import jsonpickle
from sequencer import Sequencer
from db.cas import CAS

app = Flask(__name__)

seq = Sequencer()

@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})


@app.route('/getpls', methods=['GET'])
def get_pls():
    msg = seq.broadcast()
    msg_enc = jsonpickle.encode(msg)
    return jsonify({'message': msg_enc})


if __name__ == "__main__":
    app.run(port=5005)
