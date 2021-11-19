from src.data_structure.structure.TreeNode import TreeNode


class BinarySearchTree:
    def __init__(self):
        self.root = None
        self.size = 0

    def length(self):
        return self.size

    def __len__(self):
        return self.size

    def __iter__(self):
        return self.root._iter_()

    def __setitem__(self, k, v):
        self.put(k, v)

    def put(self, key, value):
        if self.root is None:
            self.root = TreeNode(key, value)
            self.size = self.size + 1
        else:
            self._put(self.root, key, value)

    def _put(self, current_node, key, value):
        if key == current_node.key:
            current_node.value = value
        elif key < current_node.key:
            if current_node.has_left_child():
                self._put(current_node.left_child, key, value)
            else:
                current_node.left_child = TreeNode(key, value, parent=current_node)
                self.size = self.size + 1
        else:
            if current_node.has_right_child():
                self._put(current_node.right_child, key, value)
            else:
                current_node.right_child = TreeNode(key, value, parent=current_node)
                self.size = self.size + 1
