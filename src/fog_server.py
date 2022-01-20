import hashlib
import logging
import secrets
from typing import List

import messages
import utils
from aes import AESCipher
from db.mt import MerkleTree
from src.db.blocks import Block


class FogServer:
    def __init__(self) -> None:
        self.messages: List[messages.Message] = []
        self.things_uid: List[str] = []
        self.keys: List[str] = []
        self.blocks: List[Block] = []
        self.count: int = 0
        print('Fog Server created!')

    def receive(self, message: messages.Message) -> None:
        match message.message_type:
            case messages.MessageType.ENROLMENT:
                is_uid_found = False
                for thing_uid in self.things_uid:
                    if thing_uid == message.content[:4]:
                        is_uid_found = True
                        break
                if not is_uid_found:
                    received_message = message.content
                    proof = received_message[:8]
                    received_message = received_message[8:]

                    decrypted_msg = AESCipher(self.keys[0]).decrypt(received_message).decode('utf-8')
                    nonce_star = utils.sxor(proof, decrypted_msg)

                    message.message_origin.receive(messages.Message(
                        hashlib.sha256(nonce_star.encode()).hexdigest(),
                        messages.MessageType.ACK))
                    self.things_uid.append(message.content[:4])
                    proof_record: List[str] = [proof]
                    block = Block(self.count, MerkleTree.generate_tree(proof_record))
                    self.count += 1
                    self.blocks.append(block)
                    message.message_origin.is_enrolled = True
                else:
                    message.message_origin.receive(
                        messages.Message("", messages.MessageType.FAIL))
            case messages.MessageType.PROOF_SLVP:
                latest_proof: str = self.blocks[self.count - 3].tree.value
                failed: bool = True
                first_lv: Block = Block(0, "")
                # for block in self.blocks[self.count - 4:self.count]:
                #     if block.tree.value is not None:
                #         if hashlib.sha256((message.content + (utils.sxor(block.tree.value[:8], message.content))).encode()).hexdigest() == block.tree.value[8:]:
                #             first_lv = block
                #             for block_t in self.blocks[self.count - 4:first_lv.id]:
                #
                n = ""
                for block in self.blocks[self.count - 4:self.count]:
                    if block.tree.value is not None and block.tree.val_type == "LV":
                        logging.debug("COMPARING " + hashlib.sha256(utils.sxor(block.tree.value[:8], message.content).encode()).hexdigest()[:8] + " AND " + latest_proof)
                        if hashlib.sha256(utils.sxor(block.tree.value[:8], message.content).encode()).hexdigest()[:8] != latest_proof:
                            continue
                        n = utils.sxor(block.tree.value[:8], message.content)
                        logging.debug("N = " + n)
                        logging.debug("AFTER N = " + hashlib.sha256((message.content + n).encode()).hexdigest())
                        logging.debug(block.tree.value)
                        if hashlib.sha256((message.content + n).encode()).hexdigest() == block.tree.value[8:]:
                            first_lv = block
                            failed = False
                            break
                if failed:
                    logging.debug("FAILED AT FIRST FOR")
                    return
                for block in self.blocks[self.count - 4:first_lv.id]:
                    if block.tree.value is not None and block.tree.val_type == "LV":
                        if block.tree.value[8:] == hashlib.sha256(utils.sxor(block.tree.value[:8], n) + n).hexdigest():
                            logging.debug("FAILED AT SECOND FOR")
                            return
                for block in self.blocks[self.count - 4:first_lv.id]:
                    if block.tree.value is not None and block.tree.val_type == "S":
                        hash_m = utils.sxor(AESCipher(n).decrypt(block.tree.value).decode('utf-8'), message.content) # Send to CAS
                        msg = [message.content]
                        block = Block(self.count, MerkleTree.generate_tree(msg))
                        self.blocks.append(block)
                        logging.debug("PROOF SENT")
            case messages.MessageType.SIGNATURE_SLVP:
                signature_record: List[str] = [message.content]
                block = Block(self.count, MerkleTree.generate_tree(signature_record))
                block.tree.val_type = "S"
                self.blocks.append(block)
                self.count += 1
            case messages.MessageType.LINKVERIFY_SLVP:
                link_verify_record: List[str] = [message.content]
                block = Block(self.count, MerkleTree.generate_tree(link_verify_record))
                block.tree.val_type = "LV"
                self.blocks.append(block)
                self.count += 1
            case _:
                pass

    def generate_key(self) -> str:
        key = secrets.token_hex(8)
        self.keys.append(key)
        return key
