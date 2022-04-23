# from typing import List
#
# from src.db.node_new import Node
from src.tree_element import TreeElement
#
#
# class MerkleTree:
#     def __init__(self, values: List[TreeElement]) -> None:
#         self.__buildTree(values)
#         self.leaves: List[Node] = [Node(None, None, "0", "0")]
#
#     def __buildTree(self, values: List[TreeElement]) -> None:
#         leaves: List[Node] = []
#         for val in values:
#             leaves.append(Node(None, None, Node.hash(val.value), val.type, val.value))
#         # leaves: List[Node] = [Node(None, None, Node.hash(e)) for e in values]
#         self.leaves = leaves
#         if len(leaves) % 2 == 1:
#             leaves.append(leaves[-1:][0])  # duplicate last elem if odd number of elements
#         self.root: Node = self.__buildTreeRec(leaves)
#
#     def __buildTreeRec(self, nodes: List[Node]) -> Node:
#         half: int = len(nodes) // 2
#
#         if len(nodes) == 2:
#             return Node(nodes[0], nodes[1], Node.hash(nodes[0].value + nodes[1].value), "0")
#
#         left: Node = self.__buildTreeRec(nodes[:half])
#         right: Node = self.__buildTreeRec(nodes[half:])
#         value: str = Node.hash(left.value + right.value)
#         return Node(left, right, value, "0")
#
#     def printTree(self) -> None:
#         self.__printTreeRec(self.root)
#
#     def __printTreeRec(self, node) -> None:
#         if node is not None:
#             print(node.value)
#             self.__printTreeRec(node.left)
#             self.__printTreeRec(node.right)
#
#     def getRootHash(self) -> str:
#         return self.root.value
#
#
#
#
#
#
#









from typing import List

from src.db.node_new import Node
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
