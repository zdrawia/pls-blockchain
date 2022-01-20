from __future__ import annotations

from typing import TYPE_CHECKING, List

from src.db.node import Node
from src.sequencer import Sequencer

if TYPE_CHECKING:
    from fog_server import FogServer

import utils
import hashlib
import messages
import logging
from aes import AESCipher
from random import randint


class Thing:
    def __init__(self, _fog_server: FogServer = None, _sequencer: Sequencer = None) -> None:
        self.messages: List[messages.Message] = []
        self.fog_server: FogServer = _fog_server
        self.sequencer: Sequencer = _sequencer
        self.key: str = self.fog_server.generate_key()
        self.uid: str = ""
        self.nonce_star: int = -1
        self.latest_proof = None
        self.latest_nonce: str = ""
        self.prev_latest_nonce: str = ""
        self.skip: bool = True
        self.is_enrolled = False
        # Sequencer
        self.link = None
        self.signature = None
        self.proof = None

        self.prev_link = None
        self.prev_signature = None
        self.prev_proof = None

    def enroll(self) -> str:
        print('Thing trying to enroll')
        # self.latest_proof = self.sequencer.latest_proof
        nonce = randint(10000000, 99999999)
        self.prev_latest_nonce = str(nonce)
        self.nonce_star = randint(10000000, 99999999)
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()
        proof = proof[:8]
        encrypted_msg = AESCipher(self.key).encrypt(utils.sxor(proof, str(self.nonce_star))).decode('utf-8')
        q = proof + encrypted_msg
        message = messages.Message(q, messages.MessageType.ENROLMENT, self)
        self.fog_server.receive(message)
        return proof[:4]

    def post(self, post_message: str) -> str:
        if not self.is_enrolled:
            return "Can not post message"
        prf = ""
        if not self.skip:
            prf = self.__send_proof_record()

        sign = self.__send_signature_record(post_message)

        lv = self.__send_link_verify_record()

        self.prev_latest_nonce = self.latest_nonce
        self.skip = False
        return "Successfully sent: \n  Signature record = " + sign + "\n  LV record = " + lv + "\n  Proof record = " + prf

    def __is_record_exists(self, record: str) -> bool:
        record_hash = Node.hash(record)
        for block in self.fog_server.blocks:
            if block.tree.value_hash == record_hash:
                return True
        return False

    def __send_proof_record(self) -> str:
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()
        proof = proof[:8]
        message = messages.Message(proof, messages.MessageType.PROOF_SLVP, self)
        self.fog_server.receive(message)
        return proof

    def __send_signature_record(self, post_message: str) -> str:
        self.latest_nonce = str(randint(10000000, 99999999))
        signature_record = AESCipher(self.prev_latest_nonce).encrypt(
            utils.sxor(hashlib.sha256(post_message.encode()).hexdigest(),
                       hashlib.sha256(self.latest_nonce.encode()).hexdigest())).decode('utf-8')
        message = messages.Message(signature_record, messages.MessageType.SIGNATURE_SLVP, self)
        while not self.__is_record_exists(signature_record):
            self.fog_server.receive(message)
        return signature_record

    def __send_link_verify_record(self) -> str:
        link_verify_record = utils.sxor(
            hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        link_verify_record = link_verify_record + hashlib.sha256((
            hashlib.sha256(self.latest_nonce.encode()).hexdigest() + self.prev_latest_nonce).encode()).hexdigest()
        message = messages.Message(link_verify_record, messages.MessageType.LINKVERIFY_SLVP, self)
        while not self.__is_record_exists(link_verify_record):
            self.fog_server.receive(message)
        return link_verify_record

    def receive(self, message: messages) -> None:
        # self.messages.append(message)
        match message.message_type:
            case messages.MessageType.ACK:
                if hashlib.sha256(str(self.nonce_star).encode()).hexdigest() == message.content:
                    self.uid = message.content[:4]
                    # confirm completion to the administrator
                else:
                    # the protocol fails
                    pass
            case messages.MessageType.FAIL:
                self.enroll()
            case messages.MessageType.PROOF_PLS:
                if self.proof is None:
                    print("Received proof = " + message.content)
                    self.proof = message.content
                else:
                    if hashlib.sha256(utils.sxor(self.prev_link, message.content).encode()).hexdigest() == self.proof:
                        print("verified")
                        print("unlock H(B) = " + utils.sxor(message.content, AESCipher(utils.sxor(self.link, message.content)).decrypt(self.prev_signature).decode('utf-8')))
                        self.prev_proof = self.proof
                        self.proof = message.content
            case messages.MessageType.LINK_PLS:
                print("Received link = " + message.content)
                self.prev_link = self.link
                self.link = message.content
            case messages.MessageType.SIGNATURE_PLS:
                print("Received signature = " + message.content)
                self.prev_signature = self.signature
                self.signature = message.content
            case _:
                pass
