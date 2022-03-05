import hashlib
import logging
import secrets
from typing import List

import messages
import utils
from aes import AESCipher
from db.mt import MerkleTree
from src.db.blocks import Block
from src.db.cas import CAS


class FogServer:
    def __init__(self, cas: CAS) -> None:
        self.messages: List[messages.Message] = []
        self.things_uid: List[str] = []
        self.keys: List[str] = []
        self.count: int = 0
        self.cas = cas
        print('Fog Server created!')

    def receive(self, message: messages.Message) -> None:
        match message.message_type:
            case messages.MessageType.ENROLMENT:
                is_uid_found = False
                for thing_uid in self.things_uid:
                    if thing_uid == message.content[:2]:
                        is_uid_found = True
                        break
                if not is_uid_found:
                    received_message = message.content
                    proof = received_message
                    received_message = received_message[64:]

                    decrypted_msg = AESCipher(self.keys[0]).decrypt(received_message)
                    nonce_star = utils.sxor(proof, decrypted_msg)

                    message.message_origin.receive(messages.Message(
                        hashlib.sha256(nonce_star.encode()).hexdigest(),
                        messages.MessageType.ACK))
                    thing_id = message.content[:2]
                    self.things_uid.append(thing_id)
                    proof_record: List[str] = [proof]
                    block = Block(self.count, MerkleTree.generate_tree(proof_record), {
                        thing_id : proof
                    })
                    self.count += 1
                    self.cas.blocks.append(block)
                    message.message_origin.is_enrolled = True
                else:
                    message.message_origin.receive(
                        messages.Message("", messages.MessageType.FAIL))
            case messages.MessageType.PROOF_SLVP:
                latest_proof: str = self.cas.blocks[self.count - 3].tree.value

                failed: bool = True
                first_lv: Block = Block(0, "")
                n = ""
                for block in self.cas.blocks[self.count - 4:self.count]:
                    if block.tree.value is not None and block.tree.val_type == "LV":
                        n = utils.sxor(block.tree.value[:8], message.content)
                        print("N = L xor Pk+1 = " + n)
                        print("H(Pk+1 || N) = " + hashlib.sha256((message.content + n).encode()).hexdigest())
                        print("V VALUE = " + block.tree.value[8:])
                        if hashlib.sha256((message.content + n).encode()).hexdigest() == block.tree.value[8:]:
                            first_lv = block
                            failed = False
                            break
                if failed:
                    return
                print(first_lv.id)
                print(self.count)
                left_border = 0
                if self.count - 4 >= 0:
                    left_border = self.count - 4
                for block in self.cas.blocks[left_border:first_lv.id]:
                    if block.tree.value is not None and block.tree.val_type == "LV":
                        if block.tree.value[8:] == hashlib.sha256(utils.sxor(block.tree.value[:8], n) + n).hexdigest():
                            return
                for block in self.cas.blocks[left_border:first_lv.id]:
                    if block.tree.value is not None and block.tree.val_type == "S":
                        hash_m = utils.sxor(AESCipher(n).decrypt(block.tree.value), message.content) # Send to CAS
                        self.cas.deploy(hash_m)
                        msg = [message.content]
                        block = Block(self.count, MerkleTree.generate_tree(msg), {
                            message.message_origin.uid : message.content
                        })
                        self.cas.blocks.append(block)
            case messages.MessageType.SIGNATURE_SLVP:
                signature_record: List[str] = [message.content]
                block = Block(self.count, MerkleTree.generate_tree(signature_record), {
                    message.message_origin.uid : message.content
                })
                block.tree.val_type = "S"
                self.cas.blocks.append(block)
                self.count += 1
            case messages.MessageType.LINKVERIFY_SLVP:
                link_verify_record: List[str] = [message.content]
                block = Block(self.count, MerkleTree.generate_tree(link_verify_record), {
                    message.message_origin.uid : message.content
                })
                block.tree.val_type = "LV"
                self.cas.blocks.append(block)
                self.count += 1
            case _:
                pass

    def generate_key(self) -> str:
        key = secrets.token_hex(8)
        self.keys.append(key)
        return key
