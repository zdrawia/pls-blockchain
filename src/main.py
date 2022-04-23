# empty
from src.db.mt_new import MerkleTree
from src.tree_element import TreeElement

elems = [TreeElement("Hello", "S"), TreeElement("mister", "LV"), TreeElement("Merkle", "P"), TreeElement("Merklse", "P")]
mtree = MerkleTree(elems)
print(mtree.getRootHash())
