import hashlib
from typing import List

from db.blocks import Block
from db.mt import MerkleTree


class CAS:
    def __init__(self):
        self.blocks: List[Block] = []
        self.map: dict[str, str] = {}

    def deploy(self, file: str) -> str:
        hashed = hashlib.sha256(file.encode()).hexdigest()
        self.map[hashed] = file
        return hashed

    def retrieve(self, _hash: str) -> str:
        return self.map[_hash]

    def get_contrib(self, block_number: int, list_of_user_ids: List[str]) -> tuple[List, List]:
        contrib_list = []
        adjunct_hashes = []
        for block in self.blocks:
            if block.id == block_number:
                adjunct_hashes = MerkleTree.get_tree(block.tree)
                for key, value in block.data.items():
                    if key in list_of_user_ids:
                        contrib_list.append(value)
        return contrib_list, adjunct_hashes
