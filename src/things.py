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
import requests
import jsonpickle
from aes import AESCipher
from random import randint


class Thing:
    def __init__(self, _fog_server: FogServer = None, _sequencer: Sequencer = None) -> None:
        self.messages: List[messages.Message] = []
        self.fog_server: FogServer = _fog_server
        self.sequencer: Sequencer = _sequencer
        self.key: str = ""  # receive K
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
        print('Thing is trying to enroll')

        response = requests.get('http://127.0.0.1:5000/generatekey')

        self.key = response.json()['message']

        # self.latest_proof = self.sequencer.latest_proof  # receive sequencer's latest Pk

        nonce = randint(10000000, 99999999)            # generate N1
        self.nonce_star = randint(10000000, 99999999)  # and another random nonce N*
        self.prev_latest_nonce = str(nonce)
        self.latest_nonce = self.nonce_star
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest() # compute P1 = H(N1)

        encrypted_msg = AESCipher(self.key).encrypt(utils.sxor(proof, str(self.nonce_star)))
        q = proof + encrypted_msg
        message = messages.Message(q, messages.MessageType.ENROLMENT, self) # send Q = P1 || Ek(P1 xor N*)

        msg_serialized = jsonpickle.encode(message)
        response = requests.post('http://127.0.0.1:5000/enroll', json=msg_serialized)

        identifier = response.json()['message']

        return identifier

    def post(self, post_message: str=None) -> str:
        print("POSTING")
        if not self.is_enrolled:
            print("firstly enroll")
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
        response = requests.get('http://127.0.0.1:5000/getblocks')
        blocks = jsonpickle.decode(response.json()['message'])
        for block in blocks:
            for leaf in block.tree.leaves:
                if leaf.value == record_hash:
                    return True
        return False

    def __send_proof_record(self) -> str:
        proof = hashlib.sha256(self.prev_latest_nonce.encode()).hexdigest()
        # proof = proof[:8]
        message = messages.Message(proof, messages.MessageType.PROOF_SLVP, self)

        msg_serialized = jsonpickle.encode(message)

        response = requests.post('http://127.0.0.1:5000/post', json=msg_serialized)

        # self.fog_server.receive(message)
        return proof

    def __send_signature_record(self, post_message: str) -> str:
        self.latest_nonce = str(randint(10000000, 99999999))

        M = AESCipher(utils.sxor(self.prev_link, self.proof)).decrypt(self.prev_signature)

        signature_record = AESCipher(self.prev_latest_nonce).encrypt(
            M
        )

        # signature_record = AESCipher(self.prev_latest_nonce).encrypt(
        #     utils.sxor(hashlib.sha256(post_message.encode()).hexdigest(),
        #                hashlib.sha256(self.latest_nonce.encode()).hexdigest())).decode('utf-8')

        message = messages.Message(signature_record, messages.MessageType.SIGNATURE_SLVP, self)
        msg_serialized = jsonpickle.encode(message)
        while not self.__is_record_exists(signature_record):
            response = requests.post('http://127.0.0.1:5000/post', json=msg_serialized)
            # self.fog_server.receive(message)
        return signature_record

    def __send_link_verify_record(self) -> str:
        link_verify_record = utils.sxor(
            hashlib.sha256(self.latest_nonce.encode()).hexdigest(), self.prev_latest_nonce)
        print("AFSADASDAS = " + str(len(link_verify_record)))

        link_verify_record = link_verify_record + hashlib.sha256((
                                                    hashlib.sha256(
                                                        self.latest_nonce.encode()).hexdigest() + self.prev_latest_nonce).encode()).hexdigest()
        message = messages.Message(link_verify_record, messages.MessageType.LINKVERIFY_SLVP, self)
        msg_serialized = jsonpickle.encode(message)
        while not self.__is_record_exists(link_verify_record):
            response = requests.post('http://127.0.0.1:5000/post', json=msg_serialized)
            # self.fog_server.receive(message)
        return link_verify_record

    def receive(self, message: messages) -> None:
        # self.messages.append(message)
        match message.message_type:
            case messages.MessageType.ACK:
                if hashlib.sha256(str(self.nonce_star).encode()).hexdigest() == message.content:
                    self.uid = message.content[:2]
                    # confirm completion to the administrator
                else:
                    # the protocol fails
                    pass
            case messages.MessageType.FAIL:
                self.enroll()
            case messages.MessageType.PROOF_PLS:
                print("Received proof")
                if self.proof is None:
                    print("Received proof = " + message.content)
                    self.proof = message.content
                else:
                    if hashlib.sha256(utils.sxor(self.prev_link, message.content).encode()).hexdigest() == self.proof:
                        print("verified")
                        unlock = utils.sxor(message.content,
                                            AESCipher(utils.sxor(self.prev_link, message.content)).decrypt(
                                                self.prev_signature))
                        print("unlock H(B) = " + unlock)
                        self.prev_proof = self.proof
                        self.proof = message.content
                    else:
                        print("can not verify")
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
