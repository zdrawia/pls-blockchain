from src.db.node import Node


class Block:
    def __init__(self, _id, tree):
        self.id: int = _id
        self.tree: Node = tree
