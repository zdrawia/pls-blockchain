from src.tree_element import TreeElement
from typing import List
from src.db.node import Node
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
                right_child = Node(None, None, left_child.value, left_child.type, left_child.msgval)

            parent_hash = Node.hash(left_child.value + right_child.value)
            parents.append(Node(left_child, right_child, parent_hash, "0", "0"))
            index += 2

        children = parents
        parents = []
    return children[0]


class MerkleTree:
    def __init__(self, data: List[TreeElement]):
        self.leaves: List[Node] = []
        self.root = self.__generate_tree(data)

    def __generate_tree(self, data_blocks: List[TreeElement]) -> Node:
        child_nodes = []

        for msg in data_blocks:
            child_nodes.append(Node(None, None, Node.hash(msg.value), msg.type, msg.value))

        self.leaves = child_nodes

        return build_tree(child_nodes)

    def print_tree(self) -> None:
        if self.root is None:
            return

        if self.root.left is None and self.root.right is None:
            print(self.root.value)

        queue = Queue()
        queue.put(self.root)
        queue.put(None)

        while not queue.empty():
            node = queue.get()
            if not (node is None):
                print(node.value)
            else:
                print()
                if not (queue.empty()):
                    queue.put(None)

            if not (node is None) and not (node.left is None):
                queue.put(node.left)

            if not (node is None) and not (node.right is None):
                queue.put(node.right)

    def get_tree(self) -> List[str]:
        if self.root is None:
            return []

        if self.root.left is None and self.root.right is None:
            return [self.root.value]

        hash_list = []
        queue = Queue()
        queue.put(self.root)
        queue.put(None)

        while not queue.empty():
            node = queue.get()
            if not (node is None):
                hash_list.append(node.value)
            else:
                if not (queue.empty()):
                    queue.put(None)

            if not (node is None) and not (node.left is None):
                queue.put(node.left)

            if not (node is None) and not (node.right is None):
                queue.put(node.right)

        return hash_list
