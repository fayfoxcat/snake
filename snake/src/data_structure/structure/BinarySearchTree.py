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

    def _get(self, key, current_node: TreeNode):
        if not current_node:
            return None
        elif current_node.key == key:
            return current_node
        elif current_node.key < key:
            return self._get(key, current_node.left_child)
        else:
            return self._get(key, current_node.right_child)

    def get(self, key):
        if self.root:
            res = self._get(key, self.root)
            if res:
                return res.value
            else:
                return None
        else:
            return None

    def __getitem__(self, item):
        return self.get(item)

    def put(self, key, value):
        if self.root is None:
            self.root = TreeNode(key, value)
            self.size = self.size + 1
        else:
            self._put(self.root, key, value)

    def _put(self, current_node, key, value):
        if key == current_node.key:
            current_node.payload = value
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

    def __contains__(self, key):
        if self._get(key, self.root):
            return True
        else:
            return False

    def remove(self, current_node: TreeNode):
        if current_node.is_leaf():
            if current_node.parent.left_child == current_node:
                current_node.parent.left_child = None
            else:
                current_node.parent.right_child = None
        else:
            if current_node.has_left_child():
                if current_node.is_left_child():
                    current_node.left_child.parent = current_node.parent
                    current_node.parent.left_child = current_node.left_child
                elif current_node.is_right_child():
                    current_node.left_child.parent = current_node.parent
                    current_node.parent.right_child = current_node.left_child
                else:
                    current_node.replace_node_date(
                        current_node.left_child.key,
                        current_node.left_child.payload,
                        current_node.left_child.left_child,
                        current_node.left_child.right_child,
                    )
            else:
                if current_node.is_left_child():
                    current_node.right_child.parent = current_node.parent
                    current_node.parent.left_child = current_node.right_child
                elif current_node.is_right_child():
                    current_node.right_child.parent = current_node.parent
                    current_node.parent.right_child = current_node.right_child
                else:
                    current_node.replace_node_date(
                        current_node.right_child.key,
                        current_node.right_child.payload,
                        current_node.right_child.left_child,
                        current_node.right_child.right_child,
                    )

    def delete(self, key):
        if self.size > 1:
            node_tree = self._get(key, self.root)
            if node_tree:
                self.remove(node_tree)
                self.size = self.size - 1
            else:
                raise Exception('错误，树中不存在该节点')
        elif self.root.key == key:
            self.root = None
            self.size = self.size - 1
        else:
            raise Exception('错误，树中不存在该节点')

    def __delitem__(self, key):
        self.delete(key)
