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
        self.blocks_hashes = ['00ff278e2bb68384339ffe69ae324d188295ca47b50b4f20e0b6aed2b66dc5c6',
                              'a0bd53bcce0ca557fd3f2ad70d0e824076c20748abd586548c80f1582e56967d',
                              '5afc64b0c7081c7f21a78e3b6b27fc53b9aa8da7734ebf249fff46dc86555f28']

    def broadcast(self):
        link = utils.sxor(hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        signature = AESCipher(self.prev_latest_nonce).encrypt(
            utils.sxor(self.get_block_digest(), hashlib.sha256(self.latest_nonce.encode()).hexdigest())).decode('utf-8')
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()

        for thing in self.things:
            thing.receive(Message(link, messages.MessageType.LINK_PLS))
            thing.receive(Message(signature, messages.MessageType.SIGNATURE_PLS))
            thing.receive(Message(proof, messages.MessageType.PROOF_PLS))

        self.prev_latest_nonce = self.latest_nonce
        self.latest_nonce = str(randint(10000000, 99999999))

    def get_block_digest(self):
        return self.blocks_hashes.pop(0)
