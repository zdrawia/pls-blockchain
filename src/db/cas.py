import hashlib
from typing import List

from db.blocks import Block
from db.mt import MerkleTree


class CAS:
    def __init__(self):
        self.blocks: List[Block] = []
        self.last_block: Block = None
        self.map: dict[str, str] = {}

    def deploy(self, file: str) -> str:
        hashed = hashlib.sha256(file.encode()).hexdigest()
        self.map[hashed] = file
        return hashed

    def retrieve(self, _hash: str) -> str:
        return self.map[_hash]

    def get_contrib(self, block_number: int, user_id: str) -> tuple[str, List]:
        contrib_list = None
        adjunct_hashes = []
        for block in self.blocks:
            if block.id == block_number:
                hashes = block.tree.get_tree()
                for key, value in block.data.items():
                    if key == user_id:
                        contrib_list.append(value)
        return contrib_list, adjunct_hashes
