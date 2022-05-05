from __future__ import annotations

import hashlib
import socket
from random import randint

import jsonpickle

from src import utils
from src.aes import AESCipher
from src.messages import Message
import messages
from typing import TYPE_CHECKING, List


class Sequencer:
    def __init__(self):
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        self.allips = [ip[-1][0] for ip in interfaces]
        self.latest_nonce = str(randint(10000000, 99999999))
        self.prev_latest_nonce = str(randint(10000000, 99999999))
        self.latest_proof = None
        self.things = []
        self.blocks_hashes = ['00ff278e2bb68384339ffe69ae324d188295ca47b50b4f20e0b6aed2b66dc5c6',
                         'a0bd53bcce0ca557fd3f2ad70d0e824076c20748abd586548c80f1582e56967d',
                         '5afc64b0c7081c7f21a78e3b6b27fc53b9aa8da7734ebf249fff46dc86555f28']

    def broadcast(self):
        link = utils.sxor(hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        signature = AESCipher(self.prev_latest_nonce).encrypt(
            utils.sxor(self.get_block_digest(), hashlib.sha256(self.latest_nonce.encode()).hexdigest()))
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()
        self.latest_proof = proof

        # for thing in self.things:
        #     thing.receive(Message(link, messages.MessageType.LINK_PLS))
        #     thing.receive(Message(signature, messages.MessageType.SIGNATURE_PLS))
        #     thing.receive(Message(proof, messages.MessageType.PROOF_PLS))

        link = Message(link, messages.MessageType.LINK_PLS)
        signature = Message(signature, messages.MessageType.SIGNATURE_PLS)
        proof = Message(proof, messages.MessageType.PROOF_PLS)

        msg_link = jsonpickle.encode(link)
        msg_signature = jsonpickle.encode(signature)
        msg_proof = jsonpickle.encode(proof)

        for ip in self.allips:
            print(f'sending on {ip}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.bind((ip, 0))
            sock.sendto(bytes(msg_link, encoding="utf-8"), ("255.255.255.255", 5005))
            sock.sendto(bytes(msg_signature, encoding="utf-8"), ("255.255.255.255", 5005))
            sock.sendto(bytes(msg_proof, encoding="utf-8"), ("255.255.255.255", 5005))
            sock.close()

        self.prev_latest_nonce = self.latest_nonce
        self.latest_nonce = str(randint(10000000, 99999999))

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
