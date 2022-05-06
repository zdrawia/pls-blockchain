import hashlib
import logging
import secrets
from typing import List

import messages
import utils
from aes import AESCipher
from db.mt import MerkleTree as MT
from src.db.blocks import Block
from src.db.cas import CAS
from src.tree_element import TreeElement


class FogServer:
    def __init__(self, cas: CAS) -> None:
        self.messages: List[messages.Message] = []
        self.things_uid: List[str] = []
        self.key: str = ""
        self.count: int = 0
        self.cas = cas
        self.block: Block = Block(self.count)
        self.tree_content: List[TreeElement] = []
        self.users_in_block = set()
        print('Fog Server created!')

    def receive(self, message: messages.Message):
        if len(self.tree_content) >= 2:
            mtree = MT(self.tree_content)
            root_hash = mtree.get_tree()[-1]
            block = Block(self.count, mtree, root_hash, len(self.things_uid), len(self.users_in_block))
            self.cas.blocks.append(block)
            self.cas.last_block = block
            self.count += 1
            print("NEW BLOCK: \nROOT = " + block.tree_hash)
            print("\nCONTRIBUTORS = " + str(len(self.things_uid)))
            self.tree_content.clear()
        match message.message_type:
            case messages.MessageType.ENROLMENT:
                is_uid_found = False
                dec_id = str((int("0x" + message.content[:2], 16)))
                for thing_uid in self.things_uid:
                    if thing_uid == dec_id:
                        is_uid_found = True
                        break
                if not is_uid_found:
                    received_message = message.content
                    proof = received_message
                    received_message = received_message[64:]

                    decrypted_msg = AESCipher(self.key).decrypt(received_message)
                    nonce_star = utils.sxor(proof, decrypted_msg)

                    message.message_origin.receive(messages.Message(
                        hashlib.sha256(nonce_star.encode()).hexdigest(),
                        messages.MessageType.ACK))

                    thing_id = dec_id
                    self.things_uid.append(thing_id)

                    self.tree_content.append(TreeElement(proof, "P"))

                    message.message_origin.is_enrolled = True

                    self.users_in_block.add(message.message_origin.uid)

                    return thing_id
                else:
                    message.message_origin.receive(
                        messages.Message("", messages.MessageType.FAIL))
            case messages.MessageType.PROOF_SLVP:
                latest_proof: str = ""

                for leaf in self.cas.blocks[self.count - 3].tree.leaves:
                    if leaf.type == "P":
                        latest_proof = leaf.msgval

                failed: bool = True
                first_lv: Block = Block(0)
                n = ""
                for block in self.cas.blocks[self.count - 4:self.count]:
                    for leaf in block.tree.leaves:
                        if leaf.msgval is not None and leaf.type == "LV":
                            n = utils.sxor(leaf.msgval[:8], message.content)
                            print("N = L xor Pk+1 = " + n)
                            print("H(Pk+1 || N) = " + hashlib.sha256((message.content + n).encode()).hexdigest())
                            print("V value = " + leaf.msgval[8:])
                            if hashlib.sha256((message.content + n).encode()).hexdigest() == leaf.msgval[8:]:
                                first_lv = block
                                failed = False
                                break

                if failed:
                    return
                left_border = 0
                if self.count - 4 >= 0:
                    left_border = self.count - 4
                for block in self.cas.blocks[left_border:first_lv.id]:
                    for leaf in block.tree.leaves:
                        if leaf.value is not None and leaf.type == "LV":
                            if leaf.msgval[8:] == hashlib.sha256((
                                    utils.sxor(leaf.msgval[:8], n) + n).encode()).hexdigest():
                                return

                for block in self.cas.blocks[left_border:first_lv.id]:
                    for leaf in block.tree.leaves:

                        if leaf.msgval is not None and leaf.type == "S":
                            # hash_m = utils.sxor(AESCipher(n).decrypt(leaf.msgval), message.content)  # Send to CAS
                            # self.cas.deploy(hash_m)

                            self.tree_content.append(TreeElement(message.content, "P"))

                            self.users_in_block.add(message.message_origin.uid)
            case messages.MessageType.SIGNATURE_SLVP:

                self.tree_content.append(TreeElement(message.content, "S"))

                self.users_in_block.add(message.message_origin.uid)
            case messages.MessageType.LINKVERIFY_SLVP:

                self.tree_content.append(TreeElement(message.content, "LV"))

                self.users_in_block.add(message.message_origin.uid)
            case messages.MessageType.GETCONTRIB:
                return self.cas.get_contrib(message.content[0], message.content[1])
            case _:
                pass

    def generate_key(self) -> str:
        key = secrets.token_hex(8)
        self.key = key
        return key
