class Node:
    def __init__(self, left, right, value_hash: str, value=None, val_type=None) -> None:
        self.left: Node = left
        self.right: Node = right
        self.value_hash = value_hash
        self.value = value
        self.val_type = val_type

    @staticmethod
    def hash(val: str) -> str:
        import hashlib
        return hashlib.sha256(val.encode('utf-8')).hexdigest()
