from typing import List

from db.node import Node
from queue import Queue


def build_tree(children: List[Node]) -> Node:
    parents = []

    while len(children) != 1:
        index = 0
        length = len(children)
        while index < length:
            left_child: Node = children[index]

            if (index + 1) < length:
                right_child = children[index + 1]
            else:
                right_child = Node(None, None, left_child.value_hash)

            parent_hash = Node.hash(left_child.value_hash + right_child.value_hash)
            parents.append(Node(left_child, right_child, parent_hash))
            index += 2

        children = parents
        parents = []
    return children[0]


class MerkleTree:

    @staticmethod
    def generate_tree(data_blocks: List[str]) -> Node:
        child_nodes = []

        for msg in data_blocks:
            child_nodes.append(Node(None, None, Node.hash(msg), msg))

        return build_tree(child_nodes)

    @staticmethod
    def print_tree(root: Node) -> None:
        if root is None:
            return

        if root.left is None and root.right is None:
            print(root.value_hash)

        queue = Queue()
        queue.put(root)
        queue.put(None)

        while not queue.empty():
            node = queue.get()
            if not (node is None):
                print(node.value_hash)
            else:
                print()
                if not (queue.empty()):
                    queue.put(None)

            if not (node is None) and not (node.left is None):
                queue.put(node.left)

            if not (node is None) and not (node.right is None):
                queue.put(node.right)

    @staticmethod
    def get_tree(root: Node) -> List[str]:
        if root is None:
            return []

        if root.left is None and root.right is None:
            return [root.value_hash]

        hash_list = []
        queue = Queue()
        queue.put(root)
        queue.put(None)

        while not queue.empty():
            node = queue.get()
            if not (node is None):
                hash_list.append(node.value_hash)
            else:
                if not (queue.empty()):
                    queue.put(None)

            if not (node is None) and not (node.left is None):
                queue.put(node.left)

            if not (node is None) and not (node.right is None):
                queue.put(node.right)
