from __future__ import annotations

import hashlib
import socket
from random import randint

import jsonpickle
import requests

from src import utils
from src.aes import AESCipher
from src.messages import Message
import messages
from typing import TYPE_CHECKING, List


class Sequencer:
    def __init__(self):
        self.latest_nonce = str(randint(10000000, 99999999))
        self.prev_latest_nonce = str(randint(10000000, 99999999))
        self.latest_proof = None
        self.things = []
        self.blocks_hashes = ['00ff278e2bb68384339ffe69ae324d188295ca47b50b4f20e0b6aed2b66dc5c6',
                              'a0bd53bcce0ca557fd3f2ad70d0e824076c20748abd586548c80f1582e56967d',
                              '5afc64b0c7081c7f21a78e3b6b27fc53b9aa8da7734ebf249fff46dc86555f28']

    def broadcast(self):

        response = requests.get('http://127.0.0.1:5000/getblockhash')

        msg = response.json()['message']

        if msg == "empty":
            return "empty", "empty", "empty"

        block = jsonpickle.decode(msg)

        # link = utils.sxor(hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        # signature = AESCipher(self.prev_latest_nonce).encrypt(
        #     utils.sxor(self.get_block_digest(), hashlib.sha256(self.latest_nonce.encode()).hexdigest()))
        # proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()
        # self.latest_proof = proof

        link = utils.sxor(hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        signature = AESCipher(self.prev_latest_nonce).encrypt(
            utils.sxor(block.tree_hash, hashlib.sha256(self.latest_nonce.encode()).hexdigest()))
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()
        self.latest_proof = proof

        link = Message(link, messages.MessageType.LINK_PLS)
        signature = Message(signature, messages.MessageType.SIGNATURE_PLS)
        proof = Message(proof, messages.MessageType.PROOF_PLS)

        self.prev_latest_nonce = self.latest_nonce
        self.latest_nonce = str(randint(10000000, 99999999))

        return link, signature, proof

    def broadcast_proof_fail_test(self):
        link = utils.sxor(hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        signature = AESCipher(self.prev_latest_nonce).encrypt(
            utils.sxor(self.get_block_digest(), hashlib.sha256(self.latest_nonce.encode()).hexdigest()))
        proof = hashlib.sha256(str(randint(10000000, 99999999)).encode()).hexdigest()

        for thing in self.things:
            thing.receive(Message(link, messages.MessageType.LINK_PLS))
            thing.receive(Message(signature, messages.MessageType.SIGNATURE_PLS))
            thing.receive(Message(proof, messages.MessageType.PROOF_PLS))

        self.prev_latest_nonce = self.latest_nonce
        self.latest_nonce = str(randint(10000000, 99999999))

    def get_block_digest(self):
        return self.blocks_hashes.pop(0)
