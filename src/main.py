from db.mt import MerkleTree
from tree_element import TreeElement
import jsonpickle

elems = [TreeElement("Hello", "S"), TreeElement("mister", "LV"), TreeElement("Merkle", "P"), TreeElement("Merklse", "P")]
mtree = MerkleTree(elems)

serialized = jsonpickle.encode(mtree)

print(serialized)

deserialized = jsonpickle.decode(serialized)

deserialized.print_tree()