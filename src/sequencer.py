from __future__ import annotations

import hashlib
from random import randint

from src import utils
from src.aes import AESCipher
from src.messages import Message
import messages
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from things import Thing


class Sequencer:
    def __init__(self, things: List[Thing]):
        self.latest_nonce = str(randint(10000000, 99999999))
        self.prev_latest_nonce = str(randint(10000000, 99999999))
        self.things = things
        self.blocks_hashes = []

    def broadcast(self):
        link = utils.sxor(hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        signature = AESCipher(self.prev_latest_nonce).encrypt(
            utils.sxor(self.get_block_digest(), hashlib.sha256(self.latest_nonce.encode()).hexdigest()))
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()

        for thing in self.things:
            thing.receive(Message(link, messages.MessageType.LINK_PLS))
            thing.receive(Message(signature, messages.MessageType.SIGNATURE_PLS))
            thing.receive(Message(proof, messages.MessageType.PROOF_PLS))

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
