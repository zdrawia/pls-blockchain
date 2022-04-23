from typing import List
import typing
import hashlib

class Node:
    def __init__(self, left, right, value: str, _type: str, msgval: str = None) -> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.type = _type
        self.msgval = msgval

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha256(val.encode('utf-8')).hexdigest()