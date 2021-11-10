from src.data_structure.structure.BinaryTree import BinaryTree

tree = BinaryTree('a')
print(tree.get_root_value())

print(tree.get_left_child())

tree.insert_left('b')

print(tree.get_left_child())
print(tree.get_left_child().get_root_value())

tree.insert_right('c')
print(tree.get_right_child().get_root_value())

tree.get_right_child().set_root_value('hello')
print(tree.get_right_child().get_root_value())