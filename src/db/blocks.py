from typing import List

from src.db.node import Node


class Block:
    def __init__(self, _id, tree, data=None):
        self.id: int = _id
        self.tree: Node = tree
        self.data: dict[str, str] = data
